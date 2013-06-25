define buddyup::gunicorn::instance($venv,
                                   $src,
                                   $wsgi_module,
                                   $enable=true,
                                   $workers=1,
                                   ) {
  $is_present = $ensure == 'present'
  # TODO: Replace this
  $rundir = $buddyup::gunicorn::rundir
  $logdir = $buddyup::gunicorn::logdir
  $owner  = $buddyup::gunicorn::owner
  $group  = $buddyup::gunicorn::group
  
  $initscript = "/etc/init.d/gunicorn-${name}"
  $pidfile    = "${rundir}/${name}.pid"
  $socket     = "unix:${rundir}/${name}.sock"
  $logfile    = "${logdir}/${name}.log"

  $init_template = $operatingsystem ? {
    /(?i)centos|fedora|redhat/ => 'buddyup/gunicorn.rhel.init.erb',
    default => fail('Platform does not have an init script')
  }
  
  file { $initscript:
    ensure  => present,
    content => template($init_template),
    mode    => 0744,
    require => File["/etc/logrotate.d/gunicorn-${name}"],
  }
  
  file { "/etc/logrotate.d/gunicorn-${name}":
    ensure => present,
    content => template('buddyup/gunicorn.logrotate.erb'),
    mode    => 0644,
  }
  
  service { "gunicorn-${name}":
    ensure => present,
    enable => $enable,
    require => File[$initscript],
  }
}
