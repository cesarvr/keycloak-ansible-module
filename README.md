# Keycloak
These Ansible collections provide a set of tools to define Keycloak configuration as code.

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

### Configuring A Single Object

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
- **name**: represents the [RESTful](https://en.wikipedia.org/wiki/Representational_state_transfer) resource name in Keycloak.
- **id**: allow us to target the field we want to use as a unique identifier.
  - In this case the unique identifier is ``id`` for the realm, but other resources may have a different unique field such as ``groups`` that uses ``name`` as the unique identifier.
- **token**: we have to provide an OpenID token with permissions to perform the operation.
- **endpoint**: the root http(s) endpoint for the Keycloak server.
- **payload**: Here we have to provide the path for the JSON template defining the resource.
- **state**: supported states are ``absent``/``present``.
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

- **name**: represents the resource name in Keycloak.
- **id**: allow us to target the field we want to use as a unique identifier.
  -  Notice that in this case we use ``username`` to uniquely identify our objects.
- **token**: we have to provide an OpenID token with permissions to perform the operation.
- **endpoint**: the root http(s) endpoint for the Keycloak server.
- **folder**: the folder where we store the resource definition.
- **state**: supported states are ``absent``/``present``.
   - **absent**: Removes matching resources from Keycloak.
   - **present**: Publish matching resources to Keycloak.

<br>

The end result: 

![](https://github.com/cesarvr/keycloak-ansible-module/blob/main/docs/users.png?raw=true)
