Client Configuration Update via Command Line
============================================

The ``updateconfig`` command line operation can be used to update a previously
provisioned client with the latest information from a management server
(ePO or OpenDXL Broker).

`NOTE: ePO-managed environments must have 4.0 (or newer) versions of
DXL ePO extensions installed.`

The ``updateconfig`` operation performs the following:

* Retrieves the latest CA certificate bundle from the server and stores it
  at the file referenced by the ``BrokerCertChain`` setting in the ``[Certs]``
  section of the ``dxlclient.config`` file.

* Retrieves the latest broker information and updates the ``[Brokers]`` and
  ``[BrokersWebSockets]`` sections of the ``dxlclient.config`` file with
  that information.

Basic Example
*************

For example::

    dxlclient updateconfig config myserver

For this example, ``config`` is the name of the directory in which the
``dxlclient.config`` file resides and ``myserver`` is the hostname or
IP address of ePO or an OpenDXL Broker.

When prompted, provide credentials for the OpenDXL Broker Management Console
or ePO (the ePO user must be an administrator)::

    Enter server username:
    Enter server password:

If the operation is successful, output similar to the following
should be displayed::

    INFO: Updating certs in config/ca-bundle.crt
    INFO: Updating DXL config file at config/dxlclient.config

To avoid the username and password prompts, supply the appropriate
command line options (``-u`` and ``-p``)::

    dxlclient updateconfig config myserver -u myuser -p mypass

Additional Options
******************

The update operation assumes that the default web server port is 8443,
the default port under which the ePO web interface and OpenDXL Broker Management
Console is hosted.

A custom port can be specified via the ``-t`` option.

For example::

    dxlclient updateconfig config myserver -t 443

The management server's certificate is validated during TLS session
negotiation. By default it is validated against the system's trusted CAs.
Management servers commonly use a certificate issued by a private CA -- an
ePO server, for example, issues its web certificate from its own server CA --
which the system does not trust. Export that CA as a PEM file (one or more
certificates concatenated) and supply it with the ``-e`` option::

    dxlclient updateconfig config myserver -e epo-ca.pem

The host name given on the command line must match the certificate; an IP
address usually does not. Validation can be disabled with ``--insecure``, which
is not recommended because it leaves the transport of the credentials and of the
returned certificates unprotected against interception.

Python 3.13 and later reject CA certificates that lack a key usage extension
(``VERIFY_X509_STRICT``). Since the CA supplied with ``-e`` is trusted
explicitly, this check is not applied to it; it remains in effect for the
system's trusted CAs.
