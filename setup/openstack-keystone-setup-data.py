#!/bin/python

ADMIN_PASSWORD='xxxx'
DEMO_PASSWORD='yyyy'
PUB_TENANT='au_tenant'
PRIV_TENANT='webunit_tenant'
DEMO_USER='webunit'
NOVA_SERVICE_PASSWORD='nova'
GLANCE_SERVICE_PASSWORD='glance'
KEYSTONE_SERVICE_PASSWORD='keystone'
SWIFT_SERVICE_PASSWORD='keystone'
QUANTUM_SERVICE_PASSWORD='keystone'
MY_REGION='Athabasca'
ENABLE_SWIFT=False
ENABLE_QUANTUM=False

CONTROLLER_ADDRESSES={'nova':{'admin':'localhost','pub':'localhost','priv':'localhost'},
                      'glance':{'admin':'localhost','pub':'localhost','priv':'localhost'},
                      'cinder':{'admin':'localhost','pub':'localhost','priv':'localhost'},
                      'keystone':{'admin':'localhost','pub':'localhost','priv':'localhost'},
                      'swift':{'admin':'localhost','pub':'localhost','priv':'localhost'},
                      'quantum':{'admin':'localhost','pub':'localhost','priv':'localhost'},
                     }


#>>> from keystoneclient.v2_0 import client
#>>> token = '012345SECRET99TOKEN012345'
#>>> endpoint = 'http://192.168.206.130:35357/v2.0'
#>>> keystone = client.Client(token=token, endpoint=endpoint)

#>>> from keystoneclient.v2_0 import client
#>>> username='adminUser'
#>>> password='secreetword'
#>>> tenant_name='openstackDemo'
#>>> auth_url='http://192.168.206.130:5000/v2.0'
#>>> keystone = client.Client(username=username, password=password,
#...                          tenant_name=tenant_name, auth_url=auth_url)

from keystoneclient.v2_0 import client
from lxml import etree

class Keystone():
    def __init__(self,god=True,**kwargs):
        if god:
            self.token=kwargs['token']
            self.endpoint=kwargs['endpoint']
            self.client = client.Client(token=self.token, endpoint=self.endpoint)
        else:
            self.username=kwargs['username']
            self.password=kwargs['password']
            self.tenant_name=kwargs['tenant']
            self.auth_url=kwargs['auth_url']

            self.client = client.Client(username=self.username, password=self.password,
                                     tenant_name=self.tenant_name, auth_url=self.auth_url)

    def role_create(self,name):
        r=self.client.roles.create(name)
        return r.id

    def tenant_create(self,name,description=""):
        t=self.client.tenants.create(tenant_name=name,description=description)
        return t.id

    def user_create(self,name,passwd,email,tenant_id=None):
        u=self.client.users.create(name=name,password=passwd,tenant_id=tenant_id,email=email)
        return u.id

    def user_role_add(self,user,role,tenant):
        self.client.roles.add_user_role(user,role,tenant)
        # return ur

    def service_create(self,name,stype,description)
        s=self.client.services.create(name,stype,description)
        return s.id

    def endpoint_create(self,region,service_id,public_url,admin_url,internal_url)
        e=self.client.endpoints.create(region=region,service_id=service_id,
                    publicurl=public_url,adminurl=admin_url,internalurl=internal_url)
        return e.id

class KeystoneXMLSetup:
    def __init__(self,config):
        self.ids={}
        f=open(config,'r')
        self.config=etree.parse(f)
        f.close()
        env=self.config.xpath('/setup/env')
        auth_nodes=env.xpath('/auth')
        if auth_nodes:
            auth_node=auth_nodes[0]
        endpoint_nodes=env.xpath('/endpoint')[0]
        if endpoint_nodes:
            endpoint_node=endpoint_nodes[0]
        if endpoint_nodes:
            endpoint=endpoint_node.attrib['uri']
            token=endpoint_node.attrib['token']
            self.k=Keystone(god=True,endpoint=endpoint,token=token)
        elif auth_nodes:
            user=auth_node.attrib['user']
            password=auth_node.attrib['password']
            tenant=auth_node.attrib['tenant']
            auth_url=auth_node.attrib['uri']
            self.k=Keystone(god=False,user=user,password=password,tenant=tenant,auth_url=auth_url)
            
        self.ids['services']={}

        self.setupTenants()
        self.setupUsers()
        self.setupRoles()
        self.setupRoleMaps()

        # self.setupServices(enable_endpoints=True)
        self.setupNova(enable_endpoints)
        self.setupEC2(enable_endpoints)
        self.setupGlance(enable_endpoints)
        self.setupKeystone(enable_endpoints)
        self.setupCinder(enable_endpoints)
        self.setupHorizon(enable_endpoints)
        if ENABLE_SWIFT: self.setupSwift(enable_endpoints)
        if ENABLE_QUANTUM: self.setupQuantum(enable_endpoints)



    def setupTenants(self):
        self.ids['tenants']={}
        tenants=self.ids['tenants']

        tenant_elements=self.config.xpath('/setup/openstack/tenants/tenant')
        for te in tenant_elements:
            tenant_name=te.attrib['name']
            tenants[tenant_name]=self.k.tenant_create(tenant_name)

    def setupUsers(self):
        self.ids['users']={}
        users=self.ids['users']

        user_elements=self.config.xpath('/setup/openstack/users/user')
        for ue in user_elements:
            user_name=ue.attrib['name']
            user_password=ue.attrib['password']
            user_email=ue.attrib['email']
            users[user_name]=self.k.user_create(user_name,user_password,user_email)

    def setupRoles(self):
        self.ids['roles']={}
        roles=self.ids['roles']

        role_elements=self.config.xpath('/setup/openstack/roles/role')
        for re in role_elements:
            role_name=te.attrib['name']
            roles[role_name]=self.k.role_create(role_name)

    def setupRoleMaps(self):
        roles=self.ids['roles']
        users=self.ids['users']
        tenants=self.ids['tenants']

        rolemap_elements=self.config.xpath('/setup/openstack/rolemaps/rolemap')

        for rme in rolemap_elements:
            user=rme.attrib['user']
            role=rme.attrib['role']
            tenant=rme.attrib['tenant']
            self.k.user_role_add(user,   role,    tenant)

    def setupServices(self,enable_endpoints=True):
        roles=self.ids['roles']
        users=self.ids['users']
        tenants=self.ids['tenants']

        services_elements=self.config.xpath('/setup/openstack/services')
        service_tenant_id=tenants[services_elements[0].attrib['tenant']]

        service_elements=self.config.xpath('/setup/openstack/services/service')
        service_elements.sort(lambda x,y : cmp(x.attrib['order'],y.attrib['order']))
        for se in service_elements:
            if se.attrib['disabled']=='False':
                continue
            sname=se.attrib['name']
            stype=se.attrib['type']
            s=se.attrib['type']
            region=se.xpath('/region')[0].attrib['name']
            service_users=se.xpath('/user')
            for u in service_users:
                uname=u.attrib['name']
                upassword=u.attrib['password']
                uemail=u.attrib['email']
                users[uname]=self.k.user_create(uname,upassword,uemail,service_tenant_id)
            if enable_endpoints:
                
                if se.xpath('/addresses'):
                    admin_nodes=se.xpath('/addresses/admin')
                    if admin_nodes:
                        admin_node=admin_nodes[0]
                    else: admin_node=None
                    public_nodes=se.xpath('/addresses/public')
                    if public_nodes:
                        public_node=public_nodes[0]
                    else: public_node=None
                    internal_nodes=se.xpath('/addresses/internal')
                    if internal_nodes:
                        internal_node=internal_nodes[0]
                    else: internal_node=None

                    if admin_node and public_node and internal_node:
                        ## if one of the addresses is undefined - can't proceed
                        self.k.endpoint_create(region,services[sname],
                            'http://'+public_node.attrib['uri_host']+public_node.attrib['uri_suff'],
                            'http://'+admin_node.attrib['uri_host']+admin_node.attrib['uri_suff'],
                            'http://'+internal_node.attrib['uri_host']+internal_node.attrib['uri_suff']
                            )



class KeystoneSetup:
    def __init__(self):
        self.ids={}
        self.k=Keystone()

        self.setupTenants(pub_tenant=PUB_TENANT,priv_tenant=PRIV_TENANT)
        self.setupUsers()
        self.setupRoles()
        self.setupRoleMaps()

        # self.setupServices(enable_endpoints=True)
        self.ids['services']={}
        self.setupNova(enable_endpoints)
        self.setupEC2(enable_endpoints)
        self.setupGlance(enable_endpoints)
        self.setupKeystone(enable_endpoints)
        self.setupCinder(enable_endpoints)
        self.setupHorizon(enable_endpoints)
        if ENABLE_SWIFT: self.setupSwift(enable_endpoints)
        if ENABLE_QUANTUM: self.setupQuantum(enable_endpoints)

    def self.setupTenants(self,pub_tenant,priv_tenant):
        self.ids['tenants']={}
        tenants=self.ids['tenants']
        tenants['admin']=self.k.tenant_create('admin')
        tenants['service']=self.k.tenant_create('service')
        tenants[pub_tenant]=self.k.tenant_create(pub_tenant)
        tenants[priv_tenant]=self.k.tenant_create(priv_tenant)

    def setupUsers(self):
        self.ids['users']={}
        users=self.ids['users']
        users['admin']=self.k.user_create('admin',ADMIN_PASSWORD,'admin@example.com')
        users[DEMO_USER]=self.k.user_create(DEMO_USER,DEMO_PASSWORD,'admin@example.com')

    def setupRoles(self):
        self.ids['roles']={}
        roles=self.ids['roles']
        roles['admin']=self.k.role_create('admin')
        roles['Member']=self.k.role_create('Member')
        roles['KeystoneAdmin']=self.k.role_create('KeystoneAdmin')
        roles['KeystoneServiceAdmin']=self.k.role_create('KeystoneServiceAdmin')
        roles['sysadmin']=self.k.role_create('sysadmin')
        roles['netadmin']=self.k.role_create('netadmin')

    def setupRoleMaps(self):
        roles=self.ids['roles']
        users=self.ids['users']
        tenants=self.ids['tenants']
        self.k.user_role_add('admin',   'admin',    'admin')
        self.k.user_role_add(DEMO_USER, 'Member',   PUB_TENANT)
        self.k.user_role_add(DEMO_USER, 'sysadmin', PUB_TENANT)
        self.k.user_role_add(DEMO_USER, 'netadmin', PUB_TENANT)
        self.k.user_role_add(DEMO_USER, 'Member',   PRIV_TENANT)
        self.k.user_role_add('admin',   'admin',    PUB_TENANT)
        self.k.user_role_add('admin',   'KeystoneAdmin',        'admin')
        self.k.user_role_add('admin',   'KeystoneServiceAdmin', 'admin')

    def setupNova(self,enable_endpoints=False):
        services=self.ids['services']
        users=self.ids['users']
        tenants=self.ids['tenants']
        roles=self.ids['roles']
        ca=CONTROLLER_ADDRESSES

        ## Nova
        services['nova']=self.k.service_create('nova','compute','Nova compute service')
        users['nova']=self.k.user_create('nova',NOVA_SERVICE_PASSWORD,'nova@example.com',tenants['service'])
        self.k.user_role_add(tenants['service'],user['nova'],role['admin'])
        if enable_endpoints:
            self.k.endpoint_create(MY_REGION,services['nova'],
                        'http://'+ca['nova']['pub']+':$(compute_port)s/v1.1/$(tenant_id)s',
                        'http://'+ca['nova']['admin']+':$(compute_port)s/v1.1/$(tenant_id)s',
                        'http://'+ca['nova']['priv']+':$(compute_port)s/v1.1/$(tenant_id)s'
                        )

    def setupEC2(self,enable_endpoints=False):
        services=self.ids['services']
        ca=CONTROLLER_ADDRESSES

        ## EC2
        services['ec2']=self.k.service_create('ec2','ec2','EC2 compatibility layer')
        if enable_endpoints:
            self.k.endpoint_create(MY_REGION,services['ec2'],
                        'http://'+ca['nova']['pub']+':8773/services/Cloud',
                        'http://'+ca['nova']['admin']+':8773/services/Admin',
                        'http://'+ca['nova']['priv']+':8773/services/Cloud'
                        )

    def setupGlance(self,enable_endpoints=False):
        services=self.ids['services']
        users=self.ids['users']
        tenants=self.ids['tenants']
        roles=self.ids['roles']
        ca=CONTROLLER_ADDRESSES

        ## Glance
        services['glance']=self.k.service_create('glance','image','Glance Image Service')
        users['glance']=self.k.user_create('glance',GLANCE_SERVICE_PASSWORD,'glance@example.com',tenants['service'])
        self.k.user_role_add(tenants['service'],user['glance'],role['admin'])
        if enable_endpoints:
            self.k.endpoint_create(MY_REGION,services['glance'],
                        'http://'+ca['glance']['pub']+':9292/v1',
                        'http://'+ca['glance']['admin']+':9292/v1',
                        'http://'+ca['glance']['priv']+':9292/v1'
                        )


    def setupKeystone(self,enable_endpoints=False):
        services=self.ids['services']
        users=self.ids['users']
        tenants=self.ids['tenants']
        roles=self.ids['roles']
        ca=CONTROLLER_ADDRESSES

        ## Keystone 
        services['keystone']=self.k.service_create('keystone','identity','Keystone Identity Service')
        users['keystone']=self.k.user_create('keystone',KEYSTONE_SERVICE_PASSWORD,'keystone@example.com',tenants['service'])
        self.k.user_role_add(tenants['service'],user['keystone'],role['admin'])
        if enable_endpoints:
            self.k.endpoint_create(MY_REGION,services['keystone'],
                        'http://'+ca['keystone']['pub']+':$(public_port)s/v2.0',
                        'http://'+ca['keystone']['admin']+':$(admin_port)s/v2.0',
                        'http://'+ca['keystone']['priv']+'$(public_port)s/v2.0'
                        )


    setupCinder=setupNovaVolume
    def setupNovaVolume(self,enable_endpoints=False):
        services=self.ids['services']
        users=self.ids['users']
        tenants=self.ids['tenants']
        roles=self.ids['roles']
        ca=CONTROLLER_ADDRESSES

        ## Nova-Volume
        services['nova-volume']=self.k.service_create('nova-volume','volume','Nova Volume Service')
        if enable_endpoints:
            self.k.endpoint_create(MY_REGION,services['nova-volume'],
                        'http://'+ca['cinder']['pub']+':8776/v1/$(tenant_id)s',
                        'http://'+ca['cinder']['admin']+':8776/v1/$(tenant_id)s',
                        'http://'+ca['cinder']['priv']+'::8776/v1/$(tenant_id)s'
                        )


    def setupHorizon(self,enable_endpoints=False):
        services=self.ids['services']
        users=self.ids['users']
        tenants=self.ids['tenants']
        roles=self.ids['roles']
        ca=CONTROLLER_ADDRESSES

        ## Horizon
        services['horizon']=self.k.service_create('horizon','dashboard','OpenStack Dashboard')

    def setupSwift(self,enable_endpoints=False):
        services=self.ids['services']
        users=self.ids['users']
        tenants=self.ids['tenants']
        roles=self.ids['roles']
        ca=CONTROLLER_ADDRESSES
        ## Swift
            
        services['swift']=self.k.service_create('swift','object-store','Swift service')
        users['swift']=self.k.user_create('swift',SWIFT_SERVICE_PASSWORD,'swift@example.com',tenants['service'])
        self.k.user_role_add(tenants['service'],user['swift'],role['admin'])
        if enable_endpoints:
            self.k.endpoint_create(MY_REGION,services['swift'],
                        'http://'+ca['swift']['pub']+':8080/v1/AUTH_$(tenant_id)s',
                        'http://'+ca['swift']['admin']+':8080/v1/AUTH_$(tenant_id)s',
                        'http://'+ca['swift']['priv']+':8080/v1/AUTH_$(tenant_id)s'
                        )

    def setupQuantum(self,enable_endpoints=False):
        services=self.ids['services']
        users=self.ids['users']
        tenants=self.ids['tenants']
        roles=self.ids['roles']
        ca=CONTROLLER_ADDRESSES
        ## Quantum
            
        services['quantum']=self.k.service_create('quantum','network','Quantum service')
        users['quantum']=self.k.user_create('quantum',QUANTUM_SERVICE_PASSWORD,'quantum@example.com',tenants['service'])
        self.k.user_role_add(tenants['service'],user['quantum'],role['admin'])
        if enable_endpoints:
            self.k.endpoint_create(MY_REGION,services['quantum'],
                        'http://'+ca['quantum']['pub']+':9696',
                        'http://'+ca['quantum']['admin']+':9696',
                        'http://'+ca['quantum']['priv']+':9696'
                        )


