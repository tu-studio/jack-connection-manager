project('jack-connection-manager',
  version: run_command('python3', '-c' , 'from src.jack_connection_manager._version import get_versions;print(get_versions()["version"])', check: true).stdout().strip())


if get_option('versioned_install')
  	install_postfix = '-' + meson.project_version()
else
	install_postfix = ''
endif

install_venv_path = get_option('prefix') / get_option('datadir') / ('jack-connection-manager' + install_postfix) / 'venv'
build_venv_path = meson.current_source_dir() / 'venv'
wheel_name = 'jack_connection_manager-' + meson.project_version() + '-py3-none-any.whl'

# --- build python wheel
# create venv (does nothing if it already exists)
run_command('python3',  '-m',  'venv', build_venv_path, check: true)

# install build
run_command('@0@/bin/pip'.format(build_venv_path),  'install', 'build', check: true)

# build wheel
run_command('@0@/bin/python3'.format(build_venv_path), '-m', 'build', '--wheel', meson.current_source_dir(), check: true)

# --- install jack-connection-manager wheel with pip
# create virtual environment
meson.add_install_script(
	'sh', '-c',
	'sudo python3 -m venv @0@; '.format(install_venv_path)
)
# use pip of the created virtual environment to install the wheel
meson.add_install_script(
	'sh', '-c',
	'sudo @0@/bin/pip install @1@; '.format(
		install_venv_path, meson.current_source_dir() / 'dist' / wheel_name)
)

# symlink jack-connection-manager binary to bindir
meson.add_install_script(
	'sh', '-c',
	'sudo ln -s -f @0@ @1@'.format(
        install_venv_path / 'bin' / 'jack-connection-manager',
        get_option('prefix') / get_option('bindir') / 'jack-connection-manager' + install_postfix)
)

if get_option('versioned_install')
	# symlink version specific jack-connection-manager binary to bindir
	meson.add_install_script(
		'sh', '-c',
		'sudo ln -s -f @0@ @1@'.format(
			get_option('prefix') / get_option('bindir') / 'jack-connection-manager' + install_postfix,
			get_option('prefix') / get_option('bindir') / 'jack-connection-manager')
)
endif

subdir('systemd')