# Keycloak
These Ansible collections provide a set of tools to define Keycloak configuration as code.

Table of contents
=================

<!--ts-->
   * [Login](#login)
      * [Example](#example)
   * [Modules](#modules)
      * [Single Object](#configuring-a-single-object)
        * [Example](#example-1)
      * [Configuring Multiple Objects](#configuring-multiple-objects)
        * [Example](#example-2)
      * [Creating Roles And Groups](#creating-roles-and-groups)
        * [Roles](#roles)
        * [Groups](#group)  
        * [Add Roles To Group](#add-roles-to-the-group)
        * [Add Users To Group](#adding-users-to-the-group)
      * [Adding Custom Flows](#adding-custom-flows)
        * [New Flow](#adding-custom-flows)   
        * [Flow Body](#flows-and-executors)   
        * [Import](#import)
<!--te-->





## Login

Before you can perform any operation you will need an OpenID token with proper permissions, to get a this token you can use the ``keycloak.login`` module.

#### Example

This module requires the [admin-cli](https://access.redhat.com/documentation/en-us/red_hat_single_sign-on/7.0/html/server_administration_guide/sso_protocols#oidc-auth-flows) OpenID client for the **master** in order to work.

```yml
tasks:
- name: Get Token
  register: session
  cesarvr.keycloak.login:
    username: your_admin_user
    password: your_password
    endpoint: 'https://my_keycloak.com'
- debug: var=session
```
Where:
- **username**: Admin username.
- **password**: Admin password.
- **endpoint**: the root http(s) endpoint for the Keycloak server.

When successful this module will return an object with the ``token`` field:

```sh
token: eyJhbGciOiJSUzI1NiIsInR5cCIgO...
```

We can reuse this value (stored in the ``session`` variable) to perform administrative work on Keycloak:

```yml
- name: Creates a realm using the obtained token
  register: result
  cesarvr.keycloak.resource:
    name: realm
    id: 'id'
    token: '{{session.result.token}}'
    endpoint: 'https://my_keycloak.com'
    payload: files/realm.json
    state: present
```

## Modules

### Single Configuration Objects

Almost every configuration in Keycloak can be tune using the  [REST API](https://en.wikipedia.org/wiki/Representational_state_transfer), and in order to cover a much as possible we can use the ``keycloak.resource`` module which targets any Keycloak configuration as long as it follows the  [HTTP method convention](https://en.wikipedia.org/wiki/Representational_state_transfer#Semantics_of_HTTP_methods).

#### Example

To create a [realm](https://access.redhat.com/documentation/en-us/red_hat_single_sign-on/7.2/html/getting_started_guide/creating_a_realm_and_user) we just need to do this:

```yml
- name: Creates a realm
  cesarvr.keycloak.resource:
    name: realm
    id: 'id'
    token: '<token-goes-Here>'
    endpoint: 'https://my_keycloak_host'
    payload: files/realm.json
    state: present    
```

Where:
- **name**: Represents the [RESTful](https://en.wikipedia.org/wiki/Representational_state_transfer) resource name in Keycloak.
- **id**: Allow us to target the field we want to use as a unique identifier.
  - In this case the unique identifier is ``id`` for the realm, but other resources may have a different unique field such as ``groups`` that uses ``name`` as the unique identifier.
- **token**: We have to provide an OpenID token with permissions to perform the operation.
- **realm**: (Optional) To target a resource in an specific realm.
- **endpoint**: The root http(s) endpoint for the Keycloak server.
- **payload**: Here we have to provide the path for the JSON template defining the resource.
- **state**: Supported states are ``absent``/``present``.
   - **absent**: Removes a resource from Keycloak.
   - **present**: Publish a resource to the server.


#### Payload

We are going to create a realm called ``heroes`` with a JSON definition like the one below:

```js
  {
    "enabled":true,
    "id":"heroes",
    "realm":"heroes"
  }
  ```

> Each resource has their own template definition for more template examples just follow [this link](https://github.com/cesarvr/keycloak-ansible-hello-world/tree/main/files).

> For additional Keycloak Realm template fields follow [this link](https://access.redhat.com/webassets/avalon/d/red-hat-single-sign-on/version-7.0.0/restapi/#_realmrepresentation).

### Configuring Multiple Objects

In order to add multiple objects we can use the ``keycloak.resources_from_folder`` module, which can publish multiple objects as long as they are from the same type.

#### Example
So in this example we want to configure a set of users into keycloak, so first we define each user in a folder like this:

![](https://github.com/cesarvr/keycloak-ansible-module/blob/main/docs/from_folder.png?raw=true)

Make sure that each file has a structure similar to this one:
```js
{
  "enabled":true,
  "attributes":{},
  "username":"batman",
  "firstName":"Bruce",
  "lastName":"Wayne",
  "emailVerified":""
}
```

> This definition represents the [Users](https://access.redhat.com/webassets/avalon/d/red-hat-single-sign-on/version-7.0.0/restapi/#_userrepresentation) resource type.

The we define the Ansible task like this:

```yml
- name: Creates Characters from files/users/DC
  resources_from_folder:
    name: users
    id: 'username'
    realm: '{{realm}}'
    token: '<token-goes-Here>'
    endpoint: 'https://another_keycloak_host:8443'
    folder: files/users/DC
    state: present
```

- **name**: Represents the resource name in Keycloak.
- **id**: Allow us to target the field we want to use as a unique identifier.
  -  Notice That in this case we use ``username`` to uniquely identify our objects.
- **token**: We have to provide an OpenID token with permissions to perform the operation.
- **realm**: (Optional) To target a resource in an specific realm.
- **endpoint**: The root http(s) endpoint for the Keycloak server.
- **folder**: The folder where we store the resource definition.
- **state**: Supported states are ``absent``/``present``.
   - **absent**: Removes matching resources from Keycloak.
   - **present**: Publish matching resources to Keycloak.

<br>

The end result: 

![](https://github.com/cesarvr/keycloak-ansible-module/blob/main/docs/users.png?raw=true)



## Creating Roles And Groups  

A Keycloak group allow us to configure a common set of attributes (for example: roles) in a way that can be shared for one or more users. To exemplify how this work and how we can automate this we are going to create the **DC** group with two roles ``hero, villain`` this way each of our users can inherith this two roles. 

The source code would look like this: 

![](https://github.com/cesarvr/keycloak-ansible-module/blob/main/docs/groups-roles-users.png?raw=true)


#### Roles 

To add the roles we can use the ``keycloak.resources_from_folder``:

```yml
- name: Adding Roles [hero, villain]   
  cesarvr.keycloak.resources_from_folder: 
    name: roles 
    id: name
    realm: 'heroes'
    token: '<token>'
    endpoint: 'https://my_keycloak_host.com' 
    folder: files/roles/
    state: present    
```

> As you can see role is a REST resource so we can use the modules above.

#### Group 

Create the group, we are going to create a single one so we use the ``keycloak.resource``:

```yml
- name: Add DC Group 
  cesarvr.keycloak.resource: 
    name: groups 
    id: name
    realm: 'heroes'
    token: '<token>'
    endpoint: 'https://keycloak_host.com' 
    payload: files/groups/dc.json
    state: present    
```

#### Add Roles To The Group

In order to add roles to the group we need to use the ``keycloak.add_roles_to_group`` module: 

```yml 
- name: Adding Roles [hero, villain] to DC group   
  register: result
  cesarvr.keycloak.add_roles_to_group: 
    group: DC 
    roles: 
      - hero 
      - villain
    realm: 'heroes'
    token: '<token>'
    endpoint: 'https://keycloak_host.com' 
    state: present    
```

Where: 

- **group**: The name of the group where we want to add the roles. 
- **roles**: Array with the role names (the roles need to exist). 
- **token**: We have to provide an OpenID token with permissions to perform the operation.
- **realm**: (Optional) to target a resource in an specific realm.
- **endpoint**: The root http(s) endpoint for the Keycloak server.
- **state**: Supported states are ``absent``/``present``.
   - **absent**: Removes matching resources from Keycloak.
   - **present**: Publish matching resources to Keycloak.


#### Adding Users To The Group

In this case we want all the DC universe users to belong to their own group, we can use the ``keycloak.join_group`` module to do that: 

```yml 
- name: DC Heroes Joining DC Group   
  cesarvr.keycloak.join_group: 
    name: DC 
    realm: '{{realm}}'
    token: '<token>'
    endpoint: 'https://keycloak_host.com' 
    folder: files/users/DC/
    state: present    
```

Where: 

- **name**: The name of the group for the users to join.  
- **realm**: (Optional) to target a resource in an specific realm.
- **token**: We have to provide an OpenID token with permissions to perform the operation.
- **endpoint**: The root http(s) endpoint for the Keycloak server.
- **folder**: The folder where we store the users definitions.
- **state**: Supported states are ``absent``/``present``.
   - **absent**: Leave the group.
   - **present**: Join the group.




## Adding Custom Flows

One of the nice features of Keycloak is the ability to customize authentication flows to add for example an additional screen for OTP, you can store this in two files. 

#### Parent Flow 

![Screenshot 2022-01-12 at 14 21 56](https://user-images.githubusercontent.com/3899337/149148305-e8eb5811-ff1b-42e3-94a8-98a068da94b4.png)

The parent flow is basically at the name of the set storing the flow steps, it has a description file similar to this



**Sample Structure**

```json
{
        "alias": "my_custom_authentication_flow",
        "builtIn": false,
        "description": "My Custom HTTP Authentication Schemes",
        "providerId": "basic-flow",
        "topLevel": true
}
```
> Let's call it ``parent-flow.json``. 



#### Flows And Executors

![Screenshot 2022-01-12 at 14 26 58](https://user-images.githubusercontent.com/3899337/149149077-c06c4d68-a670-4dcb-a640-df9a94a35826.png)

Once we got our parent flow, we can customize its behaviour by adding new flows and executors for more info on this you can take a look at the [official documentation](https://access.redhat.com/documentation/en-us/red_hat_single_sign-on/7.2/html/server_administration_guide/authentication#authentication-flows).

**Sample Structure**
```json
[
    {
        "authenticationFlow": true,
        "configurable": false,
        "displayName": "_xx1_",
        "flowId": "a9e6371b-e6fb-44d0-8994-9c1e66ba0ced",
        "id": "3bbe9680-70d9-4334-afd8-dd6d3d453fd0",
        "index": 0,
        "level": 0,
        "requirement": "REQUIRED",
        "requirementChoices": [
            "ALTERNATIVE",
            "REQUIRED",
            "DISABLED"
        ]
    },
    ...
 ]
```

#### Publishing 
Once you got this two objects then you can use the module to define a [custom flow](https://access.redhat.com/documentation/en-us/red_hat_single_sign-on/7.2/html/server_administration_guide/authentication#authentication-flows) like this: 


```yml
  - name: Adding Custom Registration
      cesarvr.keycloak.authentication_flow: 
        name: authentication 
        parent_flow: files/my-custom-registration/parent-flow.json
        realm: '{{realm}}'
        token: '{{session.result.token}}'
        endpoint: '{{endpoint_rhsso}}' 
        payload: files/my-custom-registration/executors/navigation-flow.json
        state: present   
```


#### Import 

Usually is not a good idea to define the flows manually using JSON, what we can do instead is to design our flow using an existing instance of Keycloak, and once we are satisfied we can import it and store it as code. To do this we can use a [Keycloak API](https://pypi.org/project/kcapi/) writen in Python using the following script: 

```python
import json
from kcapi import OpenID, Keycloak

ENDPOINT = 'https://your-keycloak-instance/'

token = OpenID.createAdminClient('user', 'password').getToken(ENDPOINT)

flows = Keycloak(token, ENDPOINT).build('authentication',realm='realm-name')
flow_steps = flows.executions({'alias': 'the_name_of_your_flow'}).all()

with open('flows.json', 'w') as fp:
    json.dump(flow_steps, fp)
```





