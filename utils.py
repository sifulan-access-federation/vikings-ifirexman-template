import hashlib
import os
import random
import re
import setup
import shutil
import subprocess
import sys
from base64 import b64encode
from binascii import hexlify
from passlib.hash import ldap_sha1
from pathlib import Path


# ================= DO NOT EDIT BEYOND THIS LINE =================

# ============ CONSTANTS ============

NULL_CONFIG='UNAVAILABLE'
SETUP_CONFIG=setup.setup_config
ADDITIONAL_REQUIREMENTS=SETUP_CONFIG.get('ADDITIONAL_REQUIREMENTS')
APPLICATION_FIELDS=SETUP_CONFIG.get('APPLICATION_FIELDS')


# ============ METHODS ============

class validate():
    # validate domain name
    def domain(domain):
        regex="^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$"
        if(re.match(regex,domain)):
            return True
        return False

    # validate namespace
    def namespace(namespace):
        charRe=re.compile(r'[^a-zA-Z0-9_-]')
        namespace=charRe.search(namespace)
        return not bool(namespace)
    
    # validate options
    def options_num(num,answer):
        num_list=[]
        if answer.isnumeric():
            if not num<1:
                a=1
                while(a<=num):
                    num_list.append(a)
                    a+=1
            answer=int(answer)
            if answer in num_list:
                return True
        return False

    # validate if manifest path is needed
    def manifest_path(manifest_path,operation_dict):
        PREP=operation_dict['PREP']
        UPDATE=operation_dict['UPDATE']
        if UPDATE or not PREP:
            if not manifest_path.is_dir():
                return False
        return True

    # validate if config file is needed
    def config_file(operation_dict):
        PREP=operation_dict['PREP']
        UPDATE=operation_dict['UPDATE']
        DESTROY=operation_dict['DESTROY']
        if PREP and not UPDATE and not DESTROY:
            return True
        return False

    # validate if setup config has been prepared
    def setup_config(app_name):
        return app_name and APPLICATION_FIELDS


# encode to b64
def encode_as_secret(variable):
    variable=b64encode(variable.encode("ascii")).decode("ascii")
    return variable


# generate django secret key
def generate_secret_key():
    secret_key="".join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)") for i in range(50)])
    return secret_key


# generate sha pw
def generate_sha_pw(password):
    pw=ldap_sha1.hash(password)
    return pw


# generate nt pw
def generate_nt_pw(password):
	hash=hashlib.new('md4', password.encode('utf-16le')).digest()
	return hexlify(hash).upper().decode("utf-8")


# generate keypair
def generate_keypair(**kwargs):
    out=kwargs.get('out','.')
    prefix=kwargs.get('prefix','sp')
    fqdn=kwargs.get('fqdn','hostname')
    years=kwargs.get('years',10)
    days=years*365
    entityid=kwargs.get('entityid')
    if not entityid:
        altname='DNS:{}'.format(fqdn)
    else:
        altname='DNS:{entityid},URI:{entityid}'.format(**{'entityid':entityid})
    sslcnf='{out}/{prefix}-cert.cnf'.format(**{'out':out,'prefix':prefix})

    # write openssl config
    with open(sslcnf,'w') as f:
        f.write(
'''# OpenSSL configuration file for creating keypair
[req]
prompt=no
default_bits=3072
encrypt_key=no
default_md=sha256
distinguished_name=dn
# PrintableStrings only
string_mask=MASK:0002
x509_extensions=ext
[dn]
CN={fqdn}
[ext]
subjectAltName={altname}
subjectKeyIdentifier=hash'''
.format(**{'fqdn':fqdn,'altname':altname})
)

    # generate keypair
    key='{out}/{prefix}-key.pem'.format(**{'out':out,'prefix':prefix})
    cert='{out}/{prefix}-cert.pem'.format(**{'out':out,'prefix':prefix})
    CMD='openssl req -config {sslcnf} -new -x509 -days {days} -keyout {key} -out {cert}'.format(**{'sslcnf':sslcnf,'days':days,'key':key,'cert':cert})
    os.system(CMD)
    # delete file sslcnf
    os.remove(sslcnf)

    # read keypair and encode to b64
    with open(key,'r') as f:
        key_content=f.read()
        # delete file key
        os.remove(key)
    with open(cert,'r') as f:
        cert_content=f.read()
        # delete file cert
        os.remove(cert)
    return {'key':encode_as_secret(key_content),'cert':encode_as_secret(cert_content)}


# generate shibboleth entity id
def generate_entity_id(fqdn):
    return 'https://{fqdn}/idp/shibboleth'.format(**{'fqdn':fqdn})


# generate random node port
def generate_node_port():
    return str(random.randint(30000,32767))


# get regular fields
def get_regular_fields(application_fields):
    regular_fields=list()
    for field in application_fields:
        if not field.special:
            regular_fields.append(field)
    return regular_fields


# special fields
def get_special_fields(application_fields):
    special_fields=list()
    for field in application_fields:
        if field.special:
            special_fields.append(field)
    return special_fields


# required fields
def get_required_fields(application_fields):
    required_fields=list()
    for field in application_fields:
        if field.required:
            required_fields.append(field)
    return required_fields


# immutable fields
def get_immutable_fields(application_fields):
    immutable_fields=list()
    for field in application_fields:
        if field.immutable:
            immutable_fields.append(field)
    return immutable_fields


# get secret fields
def get_secret_fields(application_fields):
    secret_fields=list()
    for field in application_fields:
        if field.secret:
            secret_fields.append(field)
    return secret_fields


# get hidden fields
def get_hidden_fields(application_fields):
    hidden_fields=list()
    for field in application_fields:
        if field.hidden:
            hidden_fields.append(field.name)
    return hidden_fields


# directories to ignore during prep manifest
def get_ignore_dirs():
    return [
        'sample',
    ]


# get script requirements
def get_requirements_list(additional_requirements):
    return [
        'kubectl',
        'passlib (pip)',
        'Host domain',
        'Existing config file (if applicable)',
        'Existing manifest (if applicable)',
    ] + additional_requirements


# get field object
def get_field_object(field_name):
    for field in APPLICATION_FIELDS:
        if field.name==field_name:
            return field
    return None


# get message
def get_message(key):
    message_dict={
        'START':'{} KUBORC SCRIPT',
        'END':'{} KUBORC SCRIPT COMPLETE',
        'EXIT':'You Have Exited The Script',
        'INVALID_OPTION':'Please Provide A Valid {}!',
        'REQUIREMENT_ERROR':'Please Fulfill The Requirements!',
        'NOT_FOUND':'No {} Were Found!',
        'WRONG_CONFIG':'Please Choose Option "Prep" To Redo Your Configuration!',
        'SETUP_INCOMPLETE':'Please Provide All Required Values In setup.py!',
        'ERROR':'An Error Occurred! - {}',
        'HEADER':'{}',
    }
    return '#=========={}==========#'.format(message_dict[key])


# get values from namespace and host
def dissect_unique_id(namespace,host):
    unique_id_split=host.split('.')
    unique_id_length=len(unique_id_split)
    # brand name
    brand_name=unique_id_split[0]
    # manifest path
    manifest_path=Path('./file/%s-%s' % (brand_name,namespace))
    # email host
    if unique_id_length>2:
        email_domain=host.replace(unique_id_split[0]+'.','')
    else:
        email_domain=host
    host_email='%s@%s' % (brand_name,email_domain)
    # ldap host
    host_ldap=''
    n=0
    for subdomain in unique_id_split:
        n+=1
        if n!=unique_id_length:
            host_ldap=host_ldap+'dc='+subdomain+','
        else:
            host_ldap=host_ldap+'dc='+subdomain
    unique_id_dict={
        'NAMESPACE':namespace,
        'HOST':host,
        'BRAND_NAME':brand_name,
        'MANIFEST_PATH':manifest_path,
        'HOST_EMAIL':host_email,
        'HOST_LDAP':host_ldap
    }
    return unique_id_dict


# find and replace tags with values
def find_and_replace_tags(content,tag_dict):
    for tag,value in tag_dict.items():
        if tag in content:
            content=content.replace(tag,value)
    return content


# prepare options and hint
def prepare_options(option_list):
    index=0
    options=''
    # prepare options
    for option in option_list:
        index+=1
        options+='\n'+str(index)+' - '+option
    options=options.replace('\n','',1)
    # prepare hints
    hint='[{}]'
    if len(option_list)>1:
        hint=hint.format('1-'+str(len(option_list)))
    else:
        hint=hint.format('1')
    return {'OPTIONS':options,'HINT':hint,'LENGTH':len(option_list)}


# get input
def get_input(option_list,**kwargs):
    header=kwargs.get('header')
    message=kwargs.get('message')
    # display header
    if header:
        print(get_message('HEADER').format(header))
    # display message
    if message:
        print(message)
    # get options
    options_dict=prepare_options(option_list)
    options=options_dict['OPTIONS']
    hint=options_dict['HINT']
    length=options_dict['LENGTH']
    # display options
    print(options)
    # get input
    value=input('Please select an option {}: '.format(hint))
    # validate input
    if not validate.options_num(length,value):
        error_message=get_message('INVALID_OPTION').format('Option')
        sys.exit(error_message)
    return value


# handle fields
def handle_field(field,update,config_dict,existing_config):
    # if field has not been handled
    if field.name not in config_dict:
        # skip ignored fields (should have existing value, default value, be not required or handled specially)
        if not field.ignore:
            # skip immutable field when updating
            if not (update and field.immutable):
                # get field input
                config_dict[field.name]=input(field.description).strip()
            else:
                # get field input if it is a new field
                if not field.name in existing_config:
                    config_dict[field.name]=input(field.description).strip()
        
        # if no field input is given
        if not config_dict.get(field.name):
            # if field exists in existing config
            if existing_config.get(field.name) and existing_config.get(field.name)!=NULL_CONFIG:
                # take existing value
                config_dict[field.name]=existing_config[field.name]
            else:
                # take default value if available
                if field.default is not None:
                    config_dict[field.name]=field.default
                # if key is not required
                elif not field.required:
                    config_dict[field.name]=NULL_CONFIG
                # special keys will be handled differently
                elif not field.special:
                    error_message=get_message('INVALID_OPTION').format(field.name)
                    sys.exit(error_message)
    return config_dict


# handle special fields
def handle_special_fields(field,update,config_dict,existing_config):
    special_keys=[
        'SECRET_KEY',
        'NODE_PORT',
        'SHA_PASS',
        'NT_PASS',
        'WIFI_SUPPORT',
        'TELEGRAM_SUPPORT',
        'SHIBBOLETH_SUPPORT',
        'EMAIL_SUPPORT',
        'USER_VERIFICATION',
    ]
    
    # if field hasn't been handled
    if field.name not in config_dict:

        # reject field if field is not recognised
        if field.name not in special_keys:
            error_message=get_message('INVALID_OPTION').format(field.name)
            sys.exit(error_message)

        # handle field regularly
        config_dict=handle_field(field,update,config_dict,existing_config)

        # get field value
        field_value=config_dict.get(field.name) # either None or NULL_CONFIG

        if field.name=='SECRET_KEY':
            if not field_value or field_value==NULL_CONFIG:
                # generate secret key
                config_dict[field.name]=generate_secret_key()
        elif field.name=='NODE_PORT':
            if not field_value or field_value==NULL_CONFIG:
                # generate node port
                config_dict[field.name]=generate_node_port()
        elif field.name=='SHA_PASS':
            dependency='DEFAULT_USER_PASS'
            if config_dict.get(dependency):
                # generate sha password
                config_dict[field.name]=generate_sha_pw(config_dict[dependency])
            else:
                error_message=get_message('INVALID_OPTION').format(dependency)
                sys.exit(error_message)
        elif field.name=='NT_PASS':
            dependency='DEFAULT_USER_PASS'
            if config_dict.get(dependency):
                # generate nt password
                config_dict[field.name]=generate_nt_pw(config_dict[dependency])
            else:
                error_message=get_message('INVALID_OPTION').format(dependency)
                sys.exit(error_message)
        elif field.name=='WIFI_SUPPORT':
            dependencies=['REALM_DOMAIN']

            for dependency in dependencies:
                if config_dict.get(field.name)=='True':
                    field_object=get_field_object(dependency)
                    if not field_object:
                        error_message=get_message('INVALID_OPTION').format(dependency)
                        sys.exit(error_message)
                    # get dependency input
                    config_dict=handle_field(field_object,update,config_dict,existing_config)
                    if (not config_dict.get(dependency) or config_dict.get(dependency)==NULL_CONFIG):
                        config_dict[field.name]='False'
            
            if (not config_dict.get(field.name) or config_dict.get(field.name)!='True'):
                config_dict[field.name]='False'
                for dependency in dependencies:
                    config_dict[dependency]=NULL_CONFIG
        elif field.name=='TELEGRAM_SUPPORT':
            dependencies=['TELEGRAM_BOT_ID','TELEGRAM_BOT_TOKEN']

            for dependency in dependencies:
                if config_dict.get(field.name)=='True':
                    field_object=get_field_object(dependency)
                    if not field_object:
                        error_message=get_message('INVALID_OPTION').format(dependency)
                        sys.exit(error_message)
                    # get dependency input
                    config_dict=handle_field(field_object,update,config_dict,existing_config)
                    if (not config_dict.get(dependency) or config_dict.get(dependency)==NULL_CONFIG):
                        config_dict[field.name]='False'
            
            if (not config_dict.get(field.name) or config_dict.get(field.name)!='True'):
                config_dict[field.name]='False'
                for dependency in dependencies:
                    config_dict[dependency]=NULL_CONFIG
        elif field.name=='EMAIL_SUPPORT':
            dependencies=['EMAIL_HOST_USER','EMAIL_HOST_PASS']

            for dependency in dependencies:
                if config_dict.get(field.name)=='True':
                    field_object=get_field_object(dependency)
                    if not field_object:
                        error_message=get_message('INVALID_OPTION').format(dependency)
                        sys.exit(error_message)
                    # get dependency input
                    config_dict=handle_field(field_object,update,config_dict,existing_config)
                    if (not config_dict.get(dependency) or config_dict.get(dependency)==NULL_CONFIG):
                        config_dict[field.name]='False'
            
            if (not config_dict.get(field.name) or config_dict.get(field.name)!='True'):
                config_dict[field.name]='False'
                for dependency in dependencies:
                    config_dict[dependency]=NULL_CONFIG
        elif field.name=='SHIBBOLETH_SUPPORT':
            dependencies=['ENTITY_ID']

            for dependency in dependencies:
                if config_dict.get(field.name)=='True':
                    field_object=get_field_object(dependency)
                    if not field_object:
                        error_message=get_message('INVALID_OPTION').format(dependency)
                        sys.exit(error_message)
                    # get dependency input
                    config_dict=handle_field(field_object,update,config_dict,existing_config)
                    if (not config_dict.get(dependency) or config_dict.get(dependency)==NULL_CONFIG):
                        config_dict[field.name]='False'
            
            if (not config_dict.get(field.name) or config_dict.get(field.name)!='True'):
                config_dict[field.name]='False'
                for dependency in dependencies:
                    config_dict[dependency]=NULL_CONFIG
                # empty keypairs
                config_dict['SHIB_SIGNING_KEY']=encode_as_secret(NULL_CONFIG)
                config_dict['SHIB_SIGNING_CERT']=encode_as_secret(NULL_CONFIG)
                config_dict['SHIB_ENCRYPT_KEY']=encode_as_secret(NULL_CONFIG)
                config_dict['SHIB_ENCRYPT_CERT']=encode_as_secret(NULL_CONFIG)
            else:
                # generate keypairs
                signing_keypair=generate_keypair(fqdn=config_dict['HOST'],entityid=config_dict['ENTITY_ID'],prefix='sp-signing')
                config_dict['SHIB_SIGNING_KEY']=signing_keypair['key']
                config_dict['SHIB_SIGNING_CERT']=signing_keypair['cert']
                encrypt_keypair=generate_keypair(fqdn=config_dict['HOST'],entityid=config_dict['ENTITY_ID'],prefix='sp-encrypt')
                config_dict['SHIB_ENCRYPT_KEY']=encrypt_keypair['key']
                config_dict['SHIB_ENCRYPT_CERT']=encrypt_keypair['cert']
        elif field.name=='USER_VERIFICATION':
            dependencies=['STAFF_REALM','STUDENT_REALM']

            if config_dict.get('SHIBBOLETH_SUPPORT')=='True' or (config_dict.get('EMAIL_SUPPORT')=='True' and config_dict.get('EMAIL_VERIFICATION')=='True'):
                config_dict[field.name]='True'
            else:
                config_dict[field.name]='False'

            for dependency in dependencies:
                if config_dict.get(field.name)=='True':
                    field_object=get_field_object(dependency)
                    if not field_object:
                        error_message=get_message('INVALID_OPTION').format(dependency)
                        sys.exit(error_message)
                    # get dependency input
                    config_dict=handle_field(field_object,update,config_dict,existing_config)
                    if (not config_dict.get(dependency) or config_dict.get(dependency)==NULL_CONFIG):
                        config_dict[field.name]='False'
            
            if (not config_dict.get(field.name) or config_dict.get(field.name)!='True'):
                config_dict[field.name]='False'
                if config_dict.get('SHIBBOLETH_SUPPORT')=='True':
                    config_dict['SHIBBOLETH_SUPPORT']='False'
                if config_dict.get('EMAIL_VERIFICATION')=='True':
                    config_dict['EMAIL_VERIFICATION']='False'
                for dependency in dependencies:
                    config_dict[dependency]=NULL_CONFIG
    return config_dict


# ============ INPUTS ============

# get requirements input
def get_requirements():
    header='REQUIREMENTS'
    message='The following requirements are required to use this script:\n'
    for requirement in get_requirements_list(ADDITIONAL_REQUIREMENTS):
        message+='\n* '+requirement
    message=message.replace('\n','',1)
    option_list=['Yes','No']
    requirements=get_input(option_list,header=header,message=message)
    return requirements


# get namespace input
def get_namespace():
    header='NAMESPACE'
    namespace=subprocess.run(['kubectl','config','view','--minify','--output','jsonpath={..namespace}'], capture_output=True, text=True).stdout
    message='Current namespace: %s' % namespace
    option_list=['Yes','No']
    correct_ns=get_input(option_list,header=header,message=message)
    if not correct_ns=="1":
        namespace="".join(input("Please put in the correct namespace: ").split())
        if not validate.namespace(namespace):
            sys.exit(get_message('INVALID_OPTION').format(header.title()))
    return namespace


# get operations input
def get_operation():
    header='OPERATION'
    option_list=['Prep [...]','Deploy','Update','Destroy']
    operation_dict={
        'PREP':False,
        'DEPLOY':False,
        'UPDATE':False,
        'DESTROY':False
    }
    operation=get_input(option_list,header=header)
    if operation=='2':
        operation_dict['DEPLOY']=True
    elif operation=='3':
        operation_dict['UPDATE']=True
    elif operation=='4':
        operation_dict['DESTROY']=True
    else:
        operation_dict['PREP']=True
        header='PREP OPERATION'
        option_list=['Prep only','Prep and deploy','Prep and update']
        prep_operation=get_input(option_list,header=header)
        if prep_operation=='2':
            operation_dict['DEPLOY']=True
        elif prep_operation=='3':
            operation_dict['UPDATE']=True
    return operation_dict


# get host input
def get_host(app_name,namespace):
    header='%s HOST' % app_name.upper()
    print(get_message('HEADER').format(header))
    host="".join(input('%s Host URL [%s.com]: ' % (app_name.title(),app_name.lower())).split()).lower()
    if not validate.domain(host):
        sys.exit(get_message('INVALID_OPTION').format('Host URL'))
    UNIQUE_ID_DICT=dissect_unique_id(namespace,host)
    return UNIQUE_ID_DICT


# verify config
def verify_config():
    option_list=['Yes','No']
    correct_config=get_input(option_list)
    if not correct_config=='1':
        sys.exit(get_message('WRONG_CONFIG'))
    return correct_config


# get existing config
def get_existing_config(config_files_dict,operation_dict):
    config_file=config_files_dict['CONFIG_FILE']
    old_config_file=config_files_dict['OLD_CONFIG_FILE']
    existing_config=read_config_file(config_file,old_config_file)
    if not existing_config:
        if not validate.config_file(operation_dict):
            sys.exit(get_message('NOT_FOUND').format('Existing Config File'))
    else:
        prep=operation_dict['PREP']
        header='EXISTING CONFIG'
        print_config(existing_config,header=header)
        if not prep:
            verify_config()
    return existing_config


# ============ CONFIGS ============

# prep config
def prep_config(unique_id_dict,update,existing_config):
    CONFIG_DICT=unique_id_dict

    # print header
    header='PREPARE NEW CONFIG'
    print(get_message('HEADER').format(header))

    # prepare hints
    for field in APPLICATION_FIELDS:
        if field.name in existing_config:
            description=field.description.format(existing_config[field.name])
        else:
            if field.default is not None:
                description=field.description.format(field.default)
            elif field.required:
                description=field.description.format('REQUIRED')
            else:
                description=field.description.format(NULL_CONFIG)
        field.description=description

    # configure regular fields
    for field in get_regular_fields(APPLICATION_FIELDS):
        CONFIG_DICT=handle_field(field,update,CONFIG_DICT,existing_config)
    
    # configure special fields
    for field in get_special_fields(APPLICATION_FIELDS):
        CONFIG_DICT=handle_special_fields(field,update,CONFIG_DICT,existing_config)
    return CONFIG_DICT


# print config
def print_config(config_dict,**kwargs):
    header=kwargs.get('header')
    hidden_fields=get_hidden_fields(APPLICATION_FIELDS)
    if header:
        print(get_message('HEADER').format(header))
    for key,value in config_dict.items():
        if not key in hidden_fields:
            print('%s : %s' % (key,value))


# backup existing config
def backup_config(config_files_dict):
    config_file=config_files_dict['CONFIG_FILE']
    backup_file=config_files_dict['OLD_CONFIG_FILE']
    if os.path.exists(config_file):
        print('Backing up current config file to %s ...' % backup_file)
        shutil.copy(config_file,backup_file)
        print('Backup complete')


# write config
def write_config(config_file,config_dict):
    with open(config_file,'w') as f:
        print('Writing new config file to %s ...' % config_file)
        for key,value in config_dict.items():
            f.write('%s=%s\n' % (key,value))


# read config file
def read_config_file(config_file,backup_file):
    config_files=[config_file,backup_file]
    for file in config_files:
        config=Path(file)
        if config.is_file():
            with open(file,'r') as f:
                config_file_contents=f.read()
                config_file_lines=config_file_contents.splitlines()
                config_dict={x.split('=',1)[0]: x.split('=',1)[1] for x in config_file_lines}
                return config_dict
    return dict()


# get config value
def get_config_value(config_key,**kwargs):
    config_file=kwargs.get('config_file')
    backup_file=kwargs.get('backup_file')
    config_dict=kwargs.get('config_dict')
    if (config_file and backup_file) and not config_dict:
        config_dict=read_config_file(config_file,backup_file)
    if config_dict:
        if config_key in config_dict:
            return config_dict[config_key]
    return None


# ============ MANIFEST ============

# prep manifest
def prep_manifest(unique_id_dict,config_dict):
    tag_dict=dict()
    manifest_path=unique_id_dict['MANIFEST_PATH']

    # if key is secret encode value
    for field in get_secret_fields(APPLICATION_FIELDS):
        if field.name in config_dict:
            config_dict[field.name]=encode_as_secret(config_dict[field.name])
    
    # prepare tag dict keys
    for key,value in config_dict.items():
        tag_dict['{{ %s }}' % key]=key
    
    # prepare tag dict values
    for key,value in tag_dict.items():
        if value in config_dict:
            tag_dict[key]=config_dict[value]

    # copy template to manifest path
    template_path="template/"
    shutil.copytree(template_path,manifest_path)
    ignore_dirs=get_ignore_dirs()

    # write new manifests
    for root,dirs,files in os.walk(manifest_path):
        for dir in ignore_dirs:
            if dir in dirs:
                print('Ignoring {} ...'.format(dir))
                dirs.remove(dir)
        for file in files:
            file_path=os.path.join(root,file)
            # read file
            with open(file_path,'r') as f:
                print('Reading manifest {} ...'.format(file_path))
                try:
                    file_contents=f.read()
                except UnicodeDecodeError:
                    print('Ignoring {} due to ** UnicodeDecodeError ** ...'.format(file_path))
                else:
                    # write file
                    with open(file_path,'w') as f:
                        # perform replacement
                        file_contents=find_and_replace_tags(file_contents,tag_dict)
                        print('Writing manifest {} ...'.format(file_path))
                        f.write(file_contents)


# ============ OPERATIONS ============

def execute_prep(unique_id_dict,operation_dict,existing_config,config_files_dict,app_name):
    brand_name=unique_id_dict['BRAND_NAME']
    manifest_path=unique_id_dict['MANIFEST_PATH']
    update=operation_dict['UPDATE']
    config_dict=prep_config(unique_id_dict,update,existing_config)
    # verify new config
    header='VERIFY NEW CONFIG'
    print_config(config_dict,header=header)
    verify_config()

    # backup existing config and write new config
    backup_config(config_files_dict)
    write_config(config_files_dict['CONFIG_FILE'],config_dict)

    # prep new manifests
    print(get_message('HEADER').format('PREPPING MANIFESTS'))
    if manifest_path.is_dir():
        print('Removing existing manifest path ...')
        shutil.rmtree(manifest_path)
    print('Prepping manifests at %s ...' % manifest_path)
    prep_manifest(unique_id_dict,config_dict)
    print('%s %s manifests have been prepped' % (brand_name,app_name))
