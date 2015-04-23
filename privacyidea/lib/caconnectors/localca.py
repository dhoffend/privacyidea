# -*- coding: utf-8 -*-
#
#  2015-04-22 Cornelius Kölbel <cornelius.koelbel@netknights.it>
#             Initial writup
#
# License:  AGPLv3
# (c) 2015. Cornelius Kölbel
#
# This code is free software; you can redistribute it and/or
# modify it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE
# License as published by the Free Software Foundation; either
# version 3 of the License, or any later version.
#
# This code is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU AFFERO GENERAL PUBLIC LICENSE for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
__doc__ = """This module contains the connectors to Certificate Authorities.
In this first implementation it is only a local certificate authority.

This module is tested in tests/test_lib_caconnector.py in the class
MachineTestCase.
"""
from privacyidea.lib.error import CAError
from OpenSSL import crypto
from subprocess import Popen, PIPE
import shlex

CA_SIGN = "openssl ca -keyfile {cakey} -cert {cacert} -config {config} " \
          "-extensions {extension} -days {days} -in {csrfile} -out {" \
          "certificate} -batch"



class LocalCAConnector(object):
    """
    This connector connects to a local CA represented by a CA certificate and
    key in the local file system.
    OpenSSL is used.
    """

    connector_type = "local"

    def __init__(self, name, config=None):
        """
        Required attributes are:
         * cakey - the private key of the CA
         * cacert - the certificate of the CA
        Optional Attributes are:
         * List of CDPs
         * List of templates
         * Key directory
         * Default key size
         * ...
        :param config: A dictionary with all necessary attributes.
        :return:
        """
        self.name = name
        self.set_config(config)

    def _check_attributes(self):
        if "cakey" not in self.config:
            raise CAError("required argument 'cakey' is missing.")
        if "cacert" not in self.config:
            raise CAError("required argument 'cacert' is missing.")

    def set_config(self, config=None):
        self.config = config or {}
        self._check_attributes()
        # The CAKEY and the CACERT are passed as filenames
        self.cakey = self.config.get("cakey")
        self.cacert = self.config.get("cacert")

    @classmethod
    def _filename_from_x509(cls, x509_name, file_extension="pem"):
        """
        return a filename from the subject from an x509 object
        :param x509_name: The X509Name object
        :type x509_name: X509Name object
        :return: filename
        :rtype: basestring
        """
        name_components = x509_name.get_components()
        filename = ""
        for (key, value) in name_components:
            filename += value+"_"
        filename = filename[:-1] + "." + file_extension
        return filename

    def sign_request(self, csr, options=None):
        """
        Signs a certificate request with the key of the CA.

        :param csr: Certificate signing request
        :type csr: PEM string
        :param options: Additional options like the validity time or the
            template
        :type options: dict
        :return: Returns the certificate
        :rtype: basestring
        """
        # Sign the certificate for one year
        options = options or {}
        days = options.get("days", 365)
        config = options.get("openssl.cnf",
                             self.config.get(
                                 "openssl.cnf", "/etc/ssl/openssl.cnf"))
        extension = options.get("extension", "server")
        csrdir = options.get("CSRDir",
                             self.config.get("CSRDir", "/tmp"))
        certificatedir = options.get("CertificateDir",
                                     self.config.get("CertificateDir", "/tmp"))

        csr_obj = crypto.load_certificate_request(crypto.FILETYPE_PEM, csr)
        csr_filename = self._filename_from_x509(csr_obj.get_subject(),
                                                file_extension="req")
        # dump the file
        f = open(csrdir + "/" + csr_filename, "w")
        f.write(csr)
        f.close()
        certificate_filename = self._filename_from_x509(csr_obj.get_subject(),
                                                        file_extension="pem")
        csr_extensions = csr_obj.get_extensions()
        #csr_filecontent = crypto.dump_certificate_request(crypto.FILETYPE_PEM,
        #                                                  csr_obj)

        cmd = CA_SIGN.format(cakey=self.cakey, cacert=self.cacert,
                             days=days, config=config, extension=extension,
                             csrfile=csrdir + "/" + csr_filename,
                             certificate=certificatedir + "/" +
                                         certificate_filename)

        # run the command
        args = shlex.split(cmd)
        p = Popen(args, cwd=None, stdout=PIPE, stderr=PIPE,)
        result, error = p.communicate()
        if p.returncode != 0:
            # Some error occurred
            raise CAError(error)
        return certificatedir + "/" + certificate_filename


    def view_pending_certs(self):
        """
        CA Manager approval
        the token/init of would not create a certificate but a
        pending certificate request, that needs to be approved by a
        CA manager. So we need some kind of approve method.
        :return:
        """
        pass

    def request_cert(self):
        """
        create key server side
        create key on client side
        via PKCS10
        :return:
        """
        pass

    def get_templates(self):
        """
        Return a list of available certificate templates
        :return:
        """
        pass

    def publish_cert(self):
        """
        The certificate might get published somewhere
        """
        pass

    def create_crl(self, publish=True):
        """
        Create and Publish the CRL.

        :param publish: Whether the CRL should be published at its CDPs
        :return: None
        """
        pass