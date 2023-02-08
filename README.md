# VIKINGS

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+
- A MySQL database

## Preflight Checklist

- [ ] Generate a secret key for the `Values.vikings.secret` setting.

    ```sh
    python -c 'import random; print("".join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)") for i in range(50)]))'
    ```

- [ ] Optional: Prepare VIKINGS portal logo. The logo should be in `png` format and have a transparent or no background. The recommended size is *x55 pixels.

- [ ] Optional: Prepare VIKINGS portal favicon. The favicon should be in `ico` format and have a transparent or no background. The recommended size is 48x48 pixels.

- [ ] Optional: Prepare VIKINGS portal background. The background image should be in `jpg` format. The recommended size is 1920x* pixels.

- [ ] Optional: Prepare custom VIKINGS portal CSS file. The CSS file should be in `css` format.

## Installation

1. Add the chart repository.

    ```sh
    helm repo add ifirexman https://sifulan-access-federation.github.io/ifirexman-charts
    ```

2. Prepare `values.yaml` file. See the [Parameters](#parameters) section for more information.

3. Run helm install. Replace `$release_name` and `$namespace` accordingly. Uncomment the `--set` and `--set-file` options if you have prepared the logo, favicon, background and/or CSS file.

    ```sh
    helm install $release_name -n $namespace --create-namespace \
        # --set vikings.logo="$(base64 logo.png)" \
        # --set vikings.favicon="$(base64 favicon.ico)" \
        # --set vikings.background="$(base64 background.jpg)" \
        # --set-file vikings.css="main.css" \
    -f values.yaml --wait ifirexman-charts/vikings
    ```

## Uninstallation

1. Run helm uninstall. Replace `$release_name` and `$namespace` accordingly.

    ```sh
    helm uninstall $release_name -n $namespace
    ```

## Upgrading

1. Update the chart repository.

    ```sh
    helm repo update ifirexman
    ```

2. Prepare `values.yaml` file. See the [Parameters](#parameters) section for more information.

3. Run helm upgrade. Replace `$release_name` and `$namespace` accordingly. Uncomment the `--set` and `--set-file` options if you have prepared the logo, favicon, background and/or CSS file.

    ```sh
    helm upgrade $release_name -n $namespace \
        # --set vikings.logo="$(base64 logo.png)" \
        # --set vikings.favicon="$(base64 favicon.ico)" \
        # --set vikings.background="$(base64 background.jpg)" \
        # --set-file vikings.css="main.css" \
    -f values.yaml --wait ifirexman-charts/vikings
    ```

## Parameters

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| db.host | string | `"mariadb.central-svcs.svc.cluster.local"` | Database server |
| db.name | string | `"ifirexman-vikings"` | Database name |
| db.password | string | `""` | Database user password |
| db.port | string | `"3306"` | Database port |
| db.type | string | `"mysql"` | Database type, `"postgresql"` or `"mysql"` |
| db.user | string | `"root"` | Database user |
| image.vikings.pullPolicy | string | `"IfNotPresent"` | Container mage pull policy |
| image.vikings.registry | string | `"ghcr.io"` | Container mage registry |
| image.vikings.repository | string | `"sifulan-access-federation/vikings-ifirexman"` | Container image repository |
| image.vikings.tag | string | `""` | Container image version. Defaults to the Chart's appVersion. |
| ingress.clusterIssuers | string | `"letsencrypt-http-prod"` | Ingress cluster issuer |
| pvc.logs.storage | string | `"50Mi"` | Logs storage size |
| pvc.logs.storageClassName | string | `"longhorn"` | Logs storage class |
| pvc.migrations.storage | string | `"50Mi"` | Migrations storage size |
| pvc.migrations.storageClassName | string | `"longhorn"` | Migrations storage class |
| replicaCount | int | `1` | Number of replicas of the VIKINGS Portal |
| resources.limits.cpu | string | `"2"` | Maximum CPU allocation |
| resources.limits.memory | string | `"2Gi"` | Maximum memory allocation |
| resources.requests.cpu | string | `"10m"` | Minimum CPU allocation |
| resources.requests.memory | string | `"10Mi"` | Minimum memory allocation |
| vikings.background | file | `""` | VIKINGS background image in `.jpg` |
| vikings.colour.hex.dark | string | `"#DB630B"` | Dark colour in HEX |
| vikings.colour.hex.light | string | `"#F9B785"` | Light colour in HEX |
| vikings.colour.hex.neutral | string | `"#F27920"` | Neutral colour in HEX |
| vikings.colour.hex.primary | string | `"#C05709"` | Primary colour in HEX |
| vikings.colour.rgba.dark | string | `"rgba(219, 99, 11, 1)"` | Dark colour in RGBA |
| vikings.colour.rgba.light | string | `"rgba(249, 183, 133, 1)"` | Light colour in RGBA |
| vikings.colour.rgba.neutral | string | `"rgba(242, 121, 32, 1)"` | Neutral colour in RGBA |
| vikings.colour.rgba.primary | string | `"rgba(192, 87, 9, 1)"` | Primary colour in RGBA |
| vikings.css | file | `""` | Custom VIKINGS `.css` |
| vikings.debug | bool | `false` | Enable debug mode |
| vikings.default.email | string | `""` | Default user email |
| vikings.default.password | string | `"ifirexman"` | Default user password |
| vikings.default.user | string | `"admin"` | Default user username |
| vikings.domain | string | `""` | VIKINGS portal domain |
| vikings.favicon | file | `""` | VIKINGS favicon image in `.ico` |
| vikings.logo | file | `""` | VIKINGS logo image in `.png` |
| vikings.secret | string | `""` | VIKINGS secret key |
| vikings.support | string | `""` | VIKINGS support email address |
