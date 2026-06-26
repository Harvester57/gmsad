# Running gmsad in Docker

This guide explains how to package and run `gmsad` inside a Docker container. 

Containerization is highly recommended for **cloud-native environments** (like Kubernetes or Docker Compose) where your applications run in containers and need to authenticate via Kerberos using a gMSA.

---

## Architecture: The Sidecar Pattern

In a containerized setup, `gmsad` runs as a **sidecar container** alongside your application container. They share a common volume where the generated service keytab is stored.

```
+-------------------------------------------------------------+
|                     Docker/Kubernetes Pod                   |
|                                                             |
|  +------------------+                 +------------------+  |
|  |                  |  Writes Keytab  |                  |  |
|  |  gmsad Container | --------------> |  App Container   |  |
|  |    (Sidecar)     |                 | (e.g. Apache/Web)|  |
|  +------------------+                 +------------------+  |
|           |                                    |            |
|           v                                    v            |
|     Shared Volume                        Shared Volume      |
|    (shared_keytabs)                     (shared_keytabs)    |
+-----------|------------------------------------|------------+
            +-----------------++-----------------+
                              ||
                              v
                      /etc/semoule.keytab
```

---

## Configuration Requirements

To run `gmsad` in a container, you need to provide:
1.  **Configuration File:** A `gmsad.conf` file containing the gMSA sections.
2.  **Kerberos Configuration:** The host's `/etc/krb5.conf` mounted read-only so that `gmsad` can resolve the AD Domain Controllers.
3.  **Machine/Server Credentials:** The server account's keytab (typically `/etc/krb5.keytab`) used to authenticate `gmsad` to Active Directory.
4.  **Shared Volume:** A volume mounted into both the `gmsad` container and the application container to store the output keytab.

### Example Configuration (`gmsad.conf`)

In a containerized environment, the application service cannot easily be reloaded by a local command (like `systemctl reload`). Therefore, you should:
*   Omit the `on_spn_rotate_cmd` and `on_upn_rotate_cmd` settings in `gmsad.conf`.
*   Let your application watch for keytab file changes natively or reload when the file changes.

```ini
[gmsad]
loglevel = INFO
check_interval = 60

[semoule]
gMSA_sAMAccountName = semoule$
gMSA_domain = CANTINE.LOCAL
gMSA_servicePrincipalNames = http/semoule.cantine.local
# Must write to the shared volume mount point
gMSA_keytab = /var/lib/gmsad/semoule.keytab

principal = couscous$@CANTINE.LOCAL
keytab = /etc/krb5.keytab
```

---

## Running with Docker Compose

An example `docker-compose.yml` is provided at the root of the project to demonstrate this layout:

```yaml
services:
  gmsad:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: gmsad
    restart: unless-stopped
    volumes:
      # Mount your configuration file
      - ./gmsad.conf:/etc/gmsad/gmsad.conf:ro
      # Mount your realm's Kerberos configuration
      - /etc/krb5.conf:/etc/krb5.conf:ro
      # Mount the machine account keytab for AD authentication
      - /etc/krb5.keytab:/etc/krb5.keytab:ro
      # Shared volume where gmsad writes the retrieved gMSA keytab
      - shared_keytabs:/var/lib/gmsad:rw

  app:
    image: alpine:latest
    container_name: gmsa_app
    depends_on:
      - gmsad
    volumes:
      - shared_keytabs:/etc/keytabs:ro
    command: >
      sh -c "echo 'Waiting for keytab...';
             while [ ! -f /etc/keytabs/semoule.keytab ]; do sleep 1; done;
             echo 'Keytab found!';
             ls -la /etc/keytabs/;
             tail -f /dev/null"

volumes:
  shared_keytabs:
```

### Starting the Stack
1.  Ensure you have placed a valid `gmsad.conf` in your local directory.
2.  Start the containers:
    ```bash
    docker compose up -d
    ```
3.  Check the logs:
    ```bash
    docker compose logs gmsad
    ```

---

## Reloading Application Containers

When the gMSA password rotates, `gmsad` updates `/var/lib/gmsad/semoule.keytab`. To make the application container load the new keys, you can choose one of the following approaches:

### Option A: File Watching (Recommended)
Configure your application or web server (e.g. via custom logic or sidecar file-watcher scripts) to monitor `/etc/keytabs/semoule.keytab` and reload/gracefully restart the service when the file modification time changes.

### Option B: Shared Process Namespace
In Kubernetes, you can enable `shareProcessNamespace: true` on the Pod. This allows the `gmsad` sidecar container to find the process ID of the main application container and send a signal:
```ini
# Inside gmsad.conf
on_spn_rotate_cmd = killall -HUP httpd
```

### Option C: Container Orchestrator Reload
If the container is granted access to the Docker socket (`/var/run/docker.sock`) or Kubernetes API, you can run a custom reload command:
```ini
# Docker-based example:
on_spn_rotate_cmd = docker exec gmsa_app httpd -k graceful
```
*(Note: Exposing the Docker socket inside a container has security implications and should be done with caution.)*
