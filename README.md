# Keycloak

Use this module to automate Keycloak configuration.


## Keycloak Resources

In Keycloak every part of the configuration is defined in the server as a [Restful Resource](https://en.wikipedia.org/wiki/Representational_state_transfer), this makes it easy for us to think about configuration. An example of this resources are: 

- clients
- roles
- groups
- components (like Federation, Realms Key Configuration, etc).
- users

This ansible module basically provides a way to store Keycloak configuration as code, so we can rebuild a Keycloak instance from scratch without visiting the UI.  

## Adding One Resource

This module ``keycloak.resource`` takes care of adding/removing a single resource into Keycloak.


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

This module ``keycloak.resources_from_folder`` publishes all the resources in a given folder path.

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
