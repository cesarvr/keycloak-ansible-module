# Keycloak

Use this module to automate Keycloak configuration.


## Login 

Before you can perform any operation you will need an OpenID token with proper permissions, all modules provide a token field in case you can obtain/inject this token by other means. 

But if you have access to the ``admin-cli`` and the ``master`` realm, the ``cesarvr.login`` module can be use to obtain a admin token: 

```yml 
- name: Login
  register: session
  cesarvr.keycloak.login:
    username: your_admin_user
    password: your_password
    endpoint: 'https://my_keycloak.com'
- debug: var=session
```

This module returns a object with the ``token`` field which stores the OpenID token: 

```sh
token: eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJQM1VOM3I4aERNNnlIeWRzNGVucjNncllRMDdYazgySEJmemRVZWx4N29JIn0.eyJqdGkiOiJlNzYyZDhjZS02ZDU5LTRjODktYWMzNi05ZTFmZTIzZDI1ODkiLCJleHAiOjE2NDA4NjI5NzQsIm5iZiI6MCwiaWF0IjoxNjQwODYyOTE0LCJpc3MiOiJodHRwczovL3Nzby1jdmFsZGV6ci1zdGFnZS5hcHBzLnNhbmRib3gtbTIubGw5ay5wMS5vcGVuc2hpZnRhcHBzLmNvbS9hdXRoL3JlYWxtcy9tYXN0ZXIiLCJzdWIiOiIxOTIwNz...

```

We can then save this object into a variable (``session`` in this example) and reuse it accross our tasks like illustrated below: 

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


## Keycloak Resources

In Keycloak every part of the configuration is defined in the server as a [Restful Resource](https://en.wikipedia.org/wiki/Representational_state_transfer), this interface will allow us to communicate to Keycloak via the [admin REST API](https://access.redhat.com/webassets/avalon/d/red-hat-single-sign-on/version-7.0.0/restapi/). 


These are a list of possible resources supported by the module: 

- clients
- roles
- groups
- components (like Federation, Realms Key Configuration, etc).
- users

> As long that a particular Keycloak configuration obeys the REST rules, they can be implemented using this module by just providing the correct definition.

[Resource definitions](https://github.com/cesarvr/keycloak-ansible-hello-world/tree/main/files).



## Adding One Resource

``keycloak.resource`` takes care of adding/removing a single resource into Keycloak.


### Usage
In this example we are going to use the resource module to create a [realm](https://access.redhat.com/documentation/en-us/red_hat_single_sign-on/7.2/html/getting_started_guide/creating_a_realm_and_user):

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

- **name**: represents the resource name in Keycloak.
- **id**: allow us to target the field we want to use as a unique identifier.
  - In this case the unique identifier is ``id`` for realm, but other resources may have a different unique field such as ``groups`` that uses ``name`` as the unique identifier.
- **token**: we have to provide a OpenID token with permissions to perform the operation.
- **endpoint**: the root http(s) endpoint for the Keycloak server.
- **payload**: Here we have to provide the path for the JSON template defining the resource. Example:

  ```json
  {
    "enabled":true,
    "id":"heroes",
    "realm":"heroes"
  }
  ```
- **state**: supported states are ``absent``/``present``.
   - **absent**: Removes a resource from Keycloak.
   - **present**: Publish a resource to the server.


## Adding Multiple Resources

``keycloak.resources_from_folder`` publishes all the resources in a given folder path.

### Usage
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
- **token**: we have to provide a OpenID token with permissions to perform the operation.
- **endpoint**: the root http(s) endpoint for the Keycloak server.
- **folder**: the folder where we store the resource definition. 
- **payload**: Here we have to provide the path for the JSON template defining the resource.
- **state**: supported states are ``absent``/``present``.
   - **absent**: Removes matching resources from Keycloak.
   - **present**: Publish matching resources to Keycloak.
