# Common packages

class common::packages {
  $packages = [
    'curl',
    'wget',
    'vim',
    'htop',
    'git',
    'unzip',
  ]

  package { $packages:
    ensure => present,
  }
}


