#!/usr/bin/env sh


# VARIABLES
if [ "$#" -eq 7 ];
then
    APP_NAME=$1
    MANIFEST_PATH=$2
    BRAND_NAME=$3
    BUILD_OPERATION=$4
    NAMESPACE=$5
    CONFIG_FILE=$6
    OLD_CONFIG_FILE=$7
else
    echo "#==========Please Use The Kuborc Script!==========#"
    exit 1
fi


# DEPLOYMENT PATHS
binaries_path="$MANIFEST_PATH/binaries"
database_path="$MANIFEST_PATH/database"
vikings_path="$MANIFEST_PATH/vikings"
# put other deployment paths here


# FUNCTIONS
function delete_manifest(){
    for var in "$@"
    do
        kubectl delete -f $var -n $NAMESPACE
    done
}

function delete_cm(){
    for var in "$@"
    do
        kubectl delete cm $var -n $NAMESPACE
    done
}

function delete_secret(){
    for var in "$@"
    do
        kubectl delete secret $var -n $NAMESPACE
    done
}

function delete_job(){
    for var in "$@"
    do
        kubectl delete job $var -n $NAMESPACE
    done
}

function apply_manifest(){
    for var in "$@"
    do
        kubectl apply -f $var -n $NAMESPACE
    done
}

function create_cm_from_file(){
    for var in "$@"
    do
        kubectl create cm $BRAND_NAME-$var --from-file $binaries_path/$var -n $NAMESPACE
    done
}

function wait_deployment(){
    kubectl rollout status deploy/$1 -n $NAMESPACE --timeout=600s
}

function wait_job(){
    kubectl wait --for=condition=complete --timeout=240s job/$1 -n $NAMESPACE
}

function wait_pvc(){
    # kubectl wait --for=condition=bound --timeout=240s pvc/$1 -n $NAMESPACE
    while [[ $(kubectl get pvc $1 -n $NAMESPACE -o 'jsonpath={..status.phase}') != "Bound" ]]; do echo "Waiting for pvc "$1" rollout to bound" && sleep 2; done
}

function reset_binaries(){
    echo "Backing up config file $CONFIG_FILE to $OLD_CONFIG_FILE ..."
    mv $OLD_CONFIG_FILE $OLD_CONFIG_FILE.tmp 2>/dev/null
    cp $CONFIG_FILE $OLD_CONFIG_FILE
    rm -f $CONFIG_FILE $OLD_CONFIG_FILE.tmp
    echo "Deleting manifests $MANIFEST_PATH ..."
    rm -rf $MANIFEST_PATH
}


# BUILD_OPERATION
if [ "$BUILD_OPERATION" = "2" ];
then
    BUILD_OPERATION="DEPLOY"
elif [ "$BUILD_OPERATION" = "3" ];
then
    BUILD_OPERATION="UPDATE"
elif [ "$BUILD_OPERATION" = "4" ];
then
    BUILD_OPERATION="DESTROY"
else
    echo "#==========Please Use The Kuborc Script!==========#"
    exit 1
fi


# DEPLOY OR UPDATE
if [ "$BUILD_OPERATION" = "DEPLOY" ] || [ "$BUILD_OPERATION" = "UPDATE" ];
then
    echo "#==========DEPLOYING $APP_NAME FOR $BRAND_NAME AT $(date +"%T")==========#"
    # UPDATE
    if [ "$BUILD_OPERATION" = "UPDATE" ];
    then
        # do this during update
        # vikings
        delete_cm $BRAND_NAME-vikings-main.css $BRAND_NAME-vikings-background.jpg $BRAND_NAME-vikings-logo.png $BRAND_NAME-vikings-site-config.conf
        delete_manifest $vikings_path/vikings-cm.yaml $vikings_path/vikings-secret.yaml $vikings_path/vikings.yaml
        delete_manifest $vikings_path/ingress.yaml
    # DEPLOY
    else
        # do this during deployment
        # vikings		
        apply_manifest $vikings_path/static-pvc.yaml
        wait_pvc $BRAND_NAME-vikings-static-pvc
        apply_manifest $vikings_path/media-pvc.yaml
        wait_pvc $BRAND_NAME-vikings-media-pvc
        apply_manifest $vikings_path/logs-pvc.yaml
        wait_pvc $BRAND_NAME-vikings-logs-pvc
        # database
        apply_manifest $database_path/database-cm.yaml $database_path/database-secret.yaml $database_path/database-createdb.yaml && \
        wait_job $BRAND_NAME-vikings-database-createdb && \
        delete_job $BRAND_NAME-vikings-database-createdb
    fi
    # UPDATE AND DEPLOY
    # do this during update or deployment
    # vikings
    create_cm_from_file vikings-site-config.conf vikings-logo.png vikings-background.jpg vikings-main.css
    apply_manifest $vikings_path/vikings-cm.yaml $vikings_path/vikings-secret.yaml $vikings_path/vikings.yaml
    wait_deployment $BRAND_NAME-vikings
    apply_manifest $vikings_path/ingress.yaml
    echo "#==========$BRAND_NAME $APP_NAME DEPLOYMENT COMPLETED AT $(date +"%T")==========#"


# DESTROY
elif [ "$BUILD_OPERATION" = "DESTROY" ];
then
    echo "#==========DESTROYING $APP_NAME FOR $BRAND_NAME AT $(date +"%T")==========#"
    # do this during destroy
    # vikings
    delete_cm $BRAND_NAME-vikings-main.css $BRAND_NAME-vikings-background.jpg $BRAND_NAME-vikings-logo.png $BRAND_NAME-vikings-site-config.conf
    delete_manifest $vikings_path/vikings.yaml $vikings_path/vikings-cm.yaml $vikings_path/vikings-secret.yaml $vikings_path/static-pvc.yaml $vikings_path/media-pvc.yaml $vikings_path/logs-pvc.yaml
    delete_manifest $vikings_path/ingress.yaml
    # database
    apply_manifest $database_path/database-dropdb.yaml && \
    wait_job $BRAND_NAME-vikings-database-dropdb && \
    delete_job $BRAND_NAME-vikings-database-dropdb && \
    delete_manifest $database_path/database-secret.yaml $database_path/database-cm.yaml

    # RESET BINARIES
    reset_binaries
    echo "#==========$BRAND_NAME $APP_NAME TEARDOWN COMPLETED AT $(date +"%T")==========#"
fi 
