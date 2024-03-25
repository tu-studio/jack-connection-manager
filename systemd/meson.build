conf_data = configuration_data()
conf_data.set('bin_dir', get_option('prefix') / get_option('bindir'))

configure_file(input : 'jack-conneeect.service.in',
                output : 'jack-conneeect.service',
                configuration: conf_data,
                install_dir: '/etc/systemd/user'
)
