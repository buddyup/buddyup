# TODO:
# * Add SSH?
# * PostgreSQL support

class buddyup($user = 'buddyup',
              $database = false,
              $monit_admin = false,
              $srcdir = undef) {
  $home = "/home/${user}"
  if $srcdir == undef {
    $srcdir_real = 
#  $requirements = "${home}/requirements.txt"

  Exec {
    path => '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
  }

  # User setup
  user { $user:
    ensure     => present,
    shell      => '/bin/bash',
    home       => $home,
    managehome => true,
  }

  class { 'webapp::python':
    owner => $user,
    group => $user,
  }

  if $operatingsystem == /(?i)ubuntu|debian/ {
    exec { 'apt-get update': }
  }
    webapp::python::instance { 'buddyup':
      if $operatingsystem == /)?i)ubuntu|debian/ {
        require      => Exec['apt-get update'],
      }
      domain       => '_',
      wsgi_module  => 'buddyup:app',
      requirements => '../env/requirements.txt',
      src          => '/buddyup/buddyup',
    }
  }
  # database {

  if $database == 'postgres' {
    class { 'buddyup::postgres': }
  }
  elsif $database != false {
    fail("Invalid database ${database}")
  }

  # } database
}
