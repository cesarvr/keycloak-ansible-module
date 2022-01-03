  ```

> Each resource has their own template definition for more template examples just follow [this link](https://github.com/cesarvr/keycloak-ansible-hello-world/tree/main/files). 

- **state**: supported states are ``absent``/``present``.
   - **absent**: Removes a resource from Keycloak.
   - **present**: Publish a resource to the server.


### Multiple Objects

In order to add multiple objects we can use the ``keycloak.resources_from_folder`` module, which can publish multiple objects as long as they are from the same type. 

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
- **payload**: Here we have to provide the path for the JSON template defining the resource.
- **state**: supported states are ``absent``/``present``.
   - **absent**: Removes matching resources from Keycloak.
   - **present**: Publish matching resources to Keycloak.

