conf_data = configuration_data()
conf_data.set('bin_dir', get_option('prefix') / get_option('bindir'))

configure_file(input : 'jack-wire-puller.service.in',
                output : 'jack-wire-puller.service',
                configuration: conf_data,
                install_dir: '/etc/systemd/user'
)
