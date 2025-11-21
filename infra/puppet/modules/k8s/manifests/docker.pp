# Docker installation

class k8s::docker {
  include docker

  docker::image { 'pause':
    image_tag => '3.9',
  }
}


