# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service


# ------------------------
# SERVICE CALLBACK EXAMPLE
# ------------------------
class ServiceCallbacks(Service):

    # The create() callback is invoked inside NCS FASTMAP and
    # must always exist.
    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')
        if service.access.exists():
            self.log.info('EPLService: Creating switch config')
            vars = ncs.template.Variables()
            vars.add('CUSTOMER_NAME', service.customer_name)
            vars.add('VLAN_NUMBER', service.vlan_number)
            vars.add('DEVICE_NAME', service.access.device_name)
            vars.add('ACCESS_PORT', service.access.access_port)
            vars.add('UPLINK_PORT', service.access.uplink_port)
            template = ncs.template.Template(service)
            template.apply('eplSwitch-template', vars)

        if service.remoteAccess.exists():
            self.log.info('EPLService: Creating remote switch config')
            vars = ncs.template.Variables()
            vars.add('CUSTOMER_NAME', service.customer_name)
            vars.add('VLAN_NUMBER', service.vlan_number)
            vars.add('DEVICE_NAME', service.remoteAccess.device_name)
            vars.add('UPLINK_PORT', service.remoteAccess.uplink_port)
            template = ncs.template.Template(service)
            template.apply('eplRemoteSwitch-template', vars)

        if service.hubRouter.exists():
            self.log.info('EPLService: Creating router config')
            vars = ncs.template.Variables()
            vars.add('VLAN_NUMBER', service.vlan_number)
            vars.add('CUSTOMER_NAME', service.customer_name)
            vars.add('DEVICE_NAME', service.hubRouter.device_name)
            vars.add('ACCESS_INTERFACE', service.hubRouter.access_interface)
            vars.add('ROUTE_DISTINGUISHER', service.hubRouter.route_distinguisher)
            vars.add('VRF_TARGET', service.hubRouter.vrf_target)
            vars.add('SITE_NUMBER', service.hubRouter.site_number)
            template = ncs.template.Template(service)
            template.apply('eplRouter-template', vars)

        if service.remoteRouter.exists():
            self.log.info('EPLService: Creating remote router config')
            vars = ncs.template.Variables()
            vars.add('VLAN_NUMBER', service.vlan_number)
            vars.add('CUSTOMER_NAME', service.customer_name)
            vars.add('DEVICE_NAME', service.remoteRouter.device_name)
            vars.add('ACCESS_INTERFACE', service.remoteRouter.access_interface)
            vars.add('ROUTE_DISTINGUISHER', service.remoteRouter.route_distinguisher)
            vars.add('VRF_TARGET', service.remoteRouter.vrf_target)
            vars.add('SITE_NUMBER', service.remoteRouter.site_number)
            template = ncs.template.Template(service)
            template.apply('eplRouter-template', vars)

    # The pre_modification() and post_modification() callbacks are optional,
    # and are invoked outside FASTMAP. pre_modification() is invoked before
    # create, update, or delete of the service, as indicated by the enum
    # ncs_service_operation op parameter. Conversely
    # post_modification() is invoked after create, update, or delete
    # of the service. These functions can be useful e.g. for
    # allocations that should be stored and existing also when the
    # service instance is removed.

    # @Service.pre_lock_create
    # def cb_pre_lock_create(self, tctx, root, service, proplist):
    #     self.log.info('Service plcreate(service=', service._path, ')')

    # @Service.pre_modification
    # def cb_pre_modification(self, tctx, op, kp, root, proplist):
    #     self.log.info('Service premod(service=', kp, ')')

    # @Service.post_modification
    # def cb_post_modification(self, tctx, op, kp, root, proplist):
    #     self.log.info('Service postmod(service=', kp, ')')


# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Main(ncs.application.Application):
    def setup(self):
        # The application class sets up logging for us. It is accessible
        # through 'self.log' and is a ncs.log.Log instance.
        self.log.info('Main RUNNING')

        # Service callbacks require a registration for a 'service point',
        # as specified in the corresponding data model.
        #
        self.register_service('eplHubRemote-servicepoint', ServiceCallbacks)

        # If we registered any callback(s) above, the Application class
        # took care of creating a daemon (related to the service/action point).

        # When this setup method is finished, all registrations are
        # considered done and the application is 'started'.

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('Main FINISHED')
