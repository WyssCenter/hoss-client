# Groups
A group is a collection of users that can be granted permissions to a Dataset. Similar to 
granting permissions to individual users, a group can be granted read-only or read-write access
to a dataset. When applied, all users in that group will gain access.

Admins can view and manipulate all groups. Privileged users can create and manipulate
groups of which they are a member. All users can see what groups they belong to.

## Managing Groups
Methods to manage groups are part of the {py:class}`hoss.auth.AuthService` class.

- {py:class}`hoss.auth.AuthService.get_group` is used to retrieve a group and its members
- {py:class}`hoss.auth.AuthService.create_group` will create a new, empty group
- {py:class}`hoss.auth.AuthService.delete_group` will delete a group. This will remove
all permissions granted by this group for all of its members
- {py:class}`hoss.auth.AuthService.add_user_to_group` will add a user to the group and apply
all permissions the group granted
- {py:class}`hoss.auth.AuthService.remove_user_from_group` will remove a user from a group and 
revoke their access from all permissions the group granted.
