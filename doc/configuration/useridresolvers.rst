.. _useridresolvers:

UserIdResolvers
---------------

.. index:: useridresolvers, LDAP, Active Directory

Each organisation or company usually has its users managed at a central location.
This is why privacyIDEA does not provide its own user management but rather
connects to existing user stores.

UserIdResolvers are connectors to those user stores, the locations, 
where the users are managed. Nowadays this can be LDAP directories or
especially Active Directory, some times FreeIPA or the Redhat 389 service.
But classically users are also located in files like /etc/passwd on 
standalone unix systems. Web services often use SQL databases as
user store.

Today with many more online cloud services SCIM is also an uprising
protocol to access userstores.

privacyIDEA already comes with UserIdResolvers to talk to all these
user stores:

 * Flatfile resolver,
 * LDAP resolver,
 * SQL resolver,
 * SCIM resolver.

.. note:: New resolver types (python modules) can be added easily. See the
   module section for this
   (:ref:`code_useridresolvers`).

You can create as many UserIdResolvers as you wish and edit existing resolvers.
When you have added all configuration data, most UIs of the UserIdResolvers have a
button "Test resolver", so that you can test your configuration before saving
it.

Starting with privacyIDEA 2.4 resolvers can be editable, i.e. you can edit
the users in the user store. Read more about this at :ref:`manage_users`.

.. note:: Using the policy ``authentication:otppin=userstore`` users can
   authenticate with the password
   from their user store, being the LDAP password, SQL password or password
   from flat file.

.. _flatfile_resolver:

Flatfile resolver
.................

.. index:: flatfile resolver

Flatfile resolvers read files like ``/etc/passwd``. 

.. note:: The file ``/etc/passwd`` does not contain the unix password.
   Thus, if you create a flatfile resolver from this file the functionality
   with ``otppin=userstore`` is not available. You can create a flatfile with
   passwords using the tool ``privacyidea-create-pwidresolver-user``.

Create a flat file like this::
   
   privacyidea-create-pwidresolver-user -u user2 -i 1002 >> /your/flat/file



LDAP resolver
.............

.. index:: LDAP resolver, OpenLDAP, Active Directory, FreeIPA, Penrose,
   Novell eDirectory

The LDAP resolver can be used to access any kind of LDAP service like
OpenLDAP, Active Directory,
FreeIPA, Penrose, Novell eDirectory.

.. figure:: images/ldap-resolver.png
   :width: 500

   *LDAP resolver configuration*

In case of Active Directory connections you might need to check the box
``No anonymous referral chasing``. The underlying LDAP library is only
able to do anonymous referral chasing. Active Directory will produce an
error in this case [#adreferrals]_.

The ``Server URI`` can contain a comma separated list of servers.
The servers are used to create a server pool and are used with a round robin
strategy [#serverpool]_.

**Example**::

   ldap://server1, ldaps://server2:1636, server3, ldaps://server4

This will create LDAP requests to

 * server1 on port 389
 * server2 on port 1636 using SSL
 * server3 on port 389
 * server4 on port 636 using SSL.

The ``Bind Type`` with Active Directory can either be chosen as "Simple" or
as "NTLM".

.. note:: When using bind type "Simple" you need to specify the Bind DN like
   *cn=administrator,cn=users,dc=domain,dc=name*. When using bind type "NTLM"
   you need to specify Bind DN like *DOMAINNAME\\username*.

The ``LoginName`` attribute is the attribute that holds the loginname. It
can be changed to your needs.

The searchfilter and the userfilter are used for forward and backward 
search the object in LDAP.

The ``searchfilter`` is used to list all possible users, that can be used
in this resolver.

The ``userfilter`` is used to find the LDAP object for a given loginname.
This is why the ``userfilter`` contains the python string replacement parameter
``%s``, which will be filled with the given loginname to find the 
LDAP object.

The ``attribute mapping`` maps LDAP object attributes to user attributes in
privacyIDEA. privacyIDEA knows the following attributes:

 * username,
 * phone,
 * mobile,
 * email,
 * surname,
 * givenname.
  
The ``UID Type`` is the unique identifier for the LDAP object. If it is left
blank, the distinguished name will be used. In case of OpenLDAP this can be
*entryUUID* and in case of Active Directory *objectGUID*.


SQL resolver
............

.. index:: SQL resolver, MySQL, PostgreSQL, Oracle, DB2, sqlite

The SQL resolver can be used to retrieve users from any kind of 
SQL database like MySQL, PostgreSQL, Oracle, DB2 or sqlite.

.. figure:: images/sql-resolver.png
   :width: 500

   *SQL resolver configuration*

In the upper frame you need to configure the SQL connection.
The SQL resolver uses `SQLAlchemy <http://sqlalchemy.org>`_ internally.
In the field ``Driver`` you need to set a driver name as defined by the
`SQLAlchemy  dialects <http://docs.sqlalchemy.org/en/rel_0_9/dialects/>`_
like "mysql" or "postgres".

In the ``SQL attributes`` frame you can specify how the users are 
identified.

The ``Database table`` contains the users. 

.. note:: At the moment only one table 
   is supported, i.e. if some of the user data like email address or telephone
   number is located in a second table, those data can not be retrieved.
  
The ``Limit`` is the SQL limit for a userlist request. This can be important
if you have several thousand user entries in the table.

The ``Attribute mapping`` defines which table column should be mapped to
which privayIDEA attribute. The known attributes are:

 * userid,
 * username,
 * phone,
 * mobile,
 * email,
 * givenname,
 * surname.

You can add an additional ``Where statement`` if you do not want to use
all users from the table.

.. note:: The ``Additional connection parameters``
   refer to the SQLAlchemy connection but are not used at the moment.

SCIM resolver
.............

.. index:: SCIM resolver

SCIM is a "System for Cross-domain Identity Management". SCIM is a REST-based 
protocol that can be used to ease identity management in the cloud.

The SCIM resolver is tested in basic functions with OSIAM [#osiam]_,
the "Open Source Idenitty & Access Management".

To connect to a SCIM service you need to provide a URL to an authentication 
server and a URL to the resource server. The authentication server is used to
authenticate the privacyIDEA server. The authentication is based on a ``client``
name and the ``Secret`` for this client.

Userinformation is then retrieved from the resource server.

The available attributes for the ``Attribute mapping`` are:

 * username,
 * givenname,
 * surname,
 * phone,
 * mobile,
 * email.

.. rubric:: Footnotes

.. [#adreferrals] http://blogs.technet.com/b/ad/archive/2009/07/06/referral-chasing.aspx
.. [#osiam] http://www.osiam.org
.. [#serverpool] https://github.com/cannatag/ldap3/blob/master/docs/manual/source/servers.rst#server-pool
