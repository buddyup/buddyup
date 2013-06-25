
define buddyup::virtualenv($ensure=present,
                            $python=system,
                            $requirements=undef,
                            $owner=undef,
                            $group=undef,) {
  $root = $name
  $python = $version ? {
    system => 'python',
    # Starts with '/', aka an absolute path
    /\/.*/   => $version,
    default  => "python${version}"
  }

  if $owner == undef {
    fail('No owner specified')
  }

  $group = $group ? {
    undef   => $owner,
    default => $group
  }

  file { $root_parent:
    ensure => directory,
    owner  => $owner,
    group  => $group,
  }

  Exec {
    user  => $owner,
    group => $group,
    cwd   => '/tmp',
  }

  # Command to create the virtualenv
  exec { "buddyup::virtualenv ${root}":
    command => "virtualenv -p `which ${python}` --distribute --no-site-packages ${root}",
    creates => root,
    require => [File[$root],
                Package['python-virtualenv']],
  }

  # Install from requirements file
  if $requirements != undef {
    exec { "buddyup::virtualenv ${root} pip":
      command => "${root}/bin/pip -r ${requirements}",
      require => Exec["buddyup::virtualenv ${root}"],
    }
  }
}
