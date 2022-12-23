resource "google_compute_address" "test_vm_ip" {
  #address      = "10.162.95.77"
  address_type = "INTERNAL"
  name         = "test-vm-ip"
  project      = "syy-gcptest01-783a"
  purpose      = "GCE_ENDPOINT"
  region       = "us-central1"
  subnetwork   = "https://www.googleapis.com/compute/v1/projects/syy-networking-8461/regions/us-central1/subnetworks/snet-prod-us-central1-static-01"
}

resource "google_compute_instance" "test_vm" {
  zone = "us-central1-a"
  boot_disk {
    auto_delete = true
    device_name = "custodian-test"
    initialize_params {
      image = "https://www.googleapis.com/compute/beta/projects/syy-shared-images-0d08/global/images/syscogold-managed-ubuntu18-20221006"
      size  = 250
      type  = "pd-standard"
    }
    mode = "READ_WRITE"
  }

  machine_type = "e2-medium"
  metadata = 
    enable-oslogin     = "true"
    # user-data          = "#infoblox-config\ntemp_license: nios IB-V825 enterprise dns dhcp cloud\nremote_console_enabled: y"
    serial-port-enable = "true"
  }
  name = "custodian-test"
  network_interface {
    network            = "https://www.googleapis.com/compute/v1/projects/syy-networking-8461/global/networks/syy-vpc-prod"
    network_ip         = "https://www.googleapis.com/compute/v1/projects/syy-gcptest01-783a/regions/us-central1/addresses/test-vm-ip"
    stack_type         = "IPV4_ONLY"
    subnetwork         = "https://www.googleapis.com/compute/v1/projects/syy-networking-8461/regions/us-central1/subnetworks/snet-prod-us-central1-static-01"
    subnetwork_project = "syy-networking-8461"
  }
  project = "syy-gcptest01-783a"
  reservation_affinity {
    type = "ANY_RESERVATION"
  }
  scheduling {
    automatic_restart   = true
    on_host_maintenance = "MIGRATE"
    provisioning_model  = "STANDARD"
  }
  depends_on = [
    google_compute_address.test_vm_ip
  ]
}