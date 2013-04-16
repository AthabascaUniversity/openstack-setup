#!/bin/python

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
import sys

class KeystoneCore():
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

    def service_create(self,name,stype,description):
        s=self.client.services.create(name,stype,description)
        return s.id

    def endpoint_create(self,region,service_id,public_url,admin_url,internal_url):
        e=self.client.endpoints.create(region=region,service_id=service_id,
                    publicurl=public_url,adminurl=admin_url,internalurl=internal_url)
        return e.id

class KeystoneDebug(KeystoneCore):
    def __init__(self,god=True,**kwargs):
        if god:
            self.token=kwargs['token']
            self.endpoint=kwargs['endpoint']
        else:
            self.username=kwargs['username']
            self.password=kwargs['password']
            self.tenant_name=kwargs['tenant']
            self.auth_url=kwargs['auth_url']

    def call(self,params):
        if self.token:
            # We're in God mode
            pre_str="keystone --token '%s' --endpoint '%s'" % (self.token,self.endpoint)
        else:
            # normal mode
            pre_str="keystone --os-username '%s' --os-password '%s' --os-tenant-name '%s' --os-auth-url '%s'" % \
                     ( self.username, self.password, self.tenant_name, self.auth_url )
                     
        print pre_str,params
   
    def role_create(self,name):
        self.call('role-create --name'+name)
        return name

    def tenant_create(self,name,description=""):
        self.call('tenant-create --name='+name+' --description="'+description+'"')
        return name

    def user_create(self,name,passwd,email,tenant_id=None):
        self.call('user-create --name="%s" --password="%s" --tenant-id="%s" --email="%s"' % \
                    (name,passwd,tenant_id,email))
        return name

    def user_role_add(self,user,role,tenant):
        self.call('add-user-role %s %s %s' % ( user, role, tenant ))
        # return ur

    def service_create(self,name,stype,description):
        self.call('service-create --name="%s" --type="%s" --description="%s"' % (name,stype,description))
        return name

    def endpoint_create(self,region,service_id,public_url,admin_url,internal_url):
        self.call('endpoint-create --region "%s" --service-id "%s" --admin-url %s --public-url %s --internal-url %s' % \
                     (region,service_id,public_url,admin_url,internal_url))
        return region+service_id

Keystone=KeystoneDebug    

class KeystoneXMLSetup:
    def __init__(self,config):
        self.ids={}
        f=open(config,'r')
        self.config=etree.parse(f)
        f.close()
        env=self.config.xpath('/setup/env')[0]
        auth_nodes=env.xpath('auth')
        print auth_nodes
        if auth_nodes:
            auth_node=auth_nodes[0]
        endpoint_nodes=env.xpath('endpoint')
        print endpoint_nodes
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
            
        

        self.setupTenants()
        self.setupUsers()
        self.setupRoles()
        self.setupRoleMaps()
        self.setupServices()

        # self.setupServices(enable_endpoints=True)
        #self.setupNova(enable_endpoints)
        #self.setupEC2(enable_endpoints)
        #self.setupGlance(enable_endpoints)
        #self.setupKeystone(enable_endpoints)
        #self.setupCinder(enable_endpoints)
        #self.setupHorizon(enable_endpoints)
        #if ENABLE_SWIFT: self.setupSwift(enable_endpoints)
        #if ENABLE_QUANTUM: self.setupQuantum(enable_endpoints)



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
            role_name=re.attrib['name']
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
        
        self.ids['services']={}
        services=self.ids['services']
        
        services_elements=self.config.xpath('/setup/openstack/services')
        service_tenant_id=tenants[services_elements[0].attrib['tenant']]

        service_elements=self.config.xpath('/setup/openstack/services/service')
        
        service_elements.sort(lambda x,y : cmp(x.attrib['order'],y.attrib['order']))
        for se in service_elements:
            if se.attrib['disabled']=='True':
                continue
            sname=se.attrib['name']
            stype=se.attrib['type']
            sdesc=se.attrib['description']
            s=se.attrib['type']
            services[sname]=self.k.service_create(sname,stype,sdesc)
            regions=se.xpath('region')
            if regions:
                region=regions[0].attrib['name']
            else:
                region=None
            service_users=se.xpath('user')
            for u in service_users:
                uname=u.attrib['name']
                upassword=u.attrib['password']
                uemail=u.attrib['email']
                users[uname]=self.k.user_create(uname,upassword,uemail,service_tenant_id)
            if enable_endpoints:
                
                if se.xpath('addresses'):
                    admin_nodes=se.xpath('addresses/address[@type="admin"]')
                    if admin_nodes:
                        admin_node=admin_nodes[0]
                    else: admin_node=None
                    public_nodes=se.xpath('addresses/address[@type="public"]')
                    if public_nodes:
                        public_node=public_nodes[0]
                    else: public_node=None
                    internal_nodes=se.xpath('addresses/address[@type="internal"]')
                    if internal_nodes:
                        internal_node=internal_nodes[0]
                    else: internal_node=None

                    ## print admin_node, public_node, internal_node
                    if admin_node is not None and public_node is not None and internal_node is not None:
                        ## if one of the addresses is undefined - can't proceed
                        self.k.endpoint_create(region,services[sname],
                            'http://'+public_node.attrib['host']+public_node.attrib['uri_suff'],
                            'http://'+admin_node.attrib['host']+admin_node.attrib['uri_suff'],
                            'http://'+internal_node.attrib['host']+internal_node.attrib['uri_suff']
                            )
                    else:
                        print "missing URLs", admin_nodes,public_nodes,internal_nodes
                            
                else:
                    print "WHAT, no addresses???"



if __name__ == '__main__':
    if len(sys.argv)<=1:
        print "Missing config parameter"
    else:
        KeystoneXMLSetup(sys.argv[1])
        
  