"""
This file is required for getting variables that will be used in this script.
Required data are:
* Application Name
* Application Field Names
* Application Field Descriptions
* Application Field Placeholders
* Which among the fields are Required
* Immutable (cannot be changed during an update)
* Secret (will be encoded as a secret)
* Ignored by generated config files
* Additional Requirements of the script
"""


# Field Class
class Field:
    def __init__(self,name,description,special=False,required=False,immutable=False,secret=False,ignore=False,hidden=False,default=None):
        # field name
        self.name=name
        # field description
        self.description=description
        # field has a special way of handling
        self.special=special
        # field is required or not
        self.required=required
        # field is editable during update or not
        self.immutable=immutable
        # field should be encrypted as a secret or not
        self.secret=secret
        # field should require input or not
        self.ignore=ignore
        # field should be displayed in print config or not
        self.hidden=hidden
        # field default value
        self.default=default

    def __str__(self):
        return self.name


# Application Name
# eg. 'APP_NAME'='My Application'
APP_NAME='VIKINGS'


# Additional Requirements
# eg. 'ADDITIONAL_REQUIREMENTS'='requirements.txt'
ADDITIONAL_REQUIREMENTS=[
    # 'REQUIREMENT'
    # eg. 'Existing PostgreSQL Database',
    'Remote MariaDB database',
]


# Application Fields
APPLICATION_FIELDS=[
    # vikings
    Field('DB_NAME', 'VIKINGS Database Name', required=True, immutable=True, default='$-vikings-maria-db'),
    Field('DB_USER', 'Remote Database User', required=True, immutable=True, secret=True, default='root'),
    Field('DB_PASS', 'Remote Database Password', required=True, secret=True, immutable=True),
    Field('SECRET_KEY', 'Django Secret Key', special=True, immutable=True, secret=True, ignore=True, hidden=True),
    # generic
    Field('SUPPORT_EMAIL', 'Support Email Address', required=True, default='support@domain.org'),
]


# ================= DO NOT EDIT BEYOND THIS LINE =================

# Application Fields
for field in APPLICATION_FIELDS:
    field.description=field.description+' [{}]: '


# Additional Fields Available
APPLICATION_FIELDS+=[
    Field('NAMESPACE', 'Kubernetes Namespace', hidden=False),
    Field('HOST', 'Application Host', hidden=False),
    Field('BRAND_NAME', 'Brand Name', hidden=True),
    Field('MANIFEST_PATH', 'Manifest Path', hidden=True),
    Field('HOST_EMAIL', 'Host Email', hidden=True),
    Field('HOST_LDAP', 'Host LDAP', hidden=True),
]


# Debug Config
def debug_config(setup_config):
    APP_NAME=setup_config['APP_NAME']
    ADDITIONAL_REQUIREMENTS=setup_config['ADDITIONAL_REQUIREMENTS']
    APPLICATION_FIELDS=setup_config['APPLICATION_FIELDS']

    print('Application Name\n---')
    if APP_NAME:
        print('%s' % APP_NAME)

    print('\nAdditional Requirements\n---')
    print(ADDITIONAL_REQUIREMENTS)

    print('\nApplication Fields\n---')
    for field in APPLICATION_FIELDS:
        print('"%s" : "%s"' % (field.name,field.description))
        print('\nField Properties\n---')
        print('Special: %s' % field.special)
        print('Required: %s' % field.required)
        print('Immutable: %s' % field.immutable)
        print('Secret: %s' % field.secret)
        print('Ignore: %s' % field.ignore)
        print('Hidden: %s' % field.hidden)
        print('Default: %s\n' % field.default)


# Setup Config Dict
setup_config={
    'APP_NAME':APP_NAME,
    'ADDITIONAL_REQUIREMENTS':ADDITIONAL_REQUIREMENTS,
    'APPLICATION_FIELDS':APPLICATION_FIELDS,
}


# debug_config(setup_config)
