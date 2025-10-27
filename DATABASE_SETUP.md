# Database Setup for New Server

## Configuration
- **New Server IP**: 80.95.207.45 (web server)
- **Database Server IP**: 80.95.207.42 (existing server)
- **Database Name**: vanrentalsnewdb
- **Username**: epc_user
- **Password**: N0rfolk

## PostgreSQL Configuration on Database Server (80.95.207.42)

### 1. Allow Remote Connections
Edit PostgreSQL configuration to allow connections from the new server:

```bash
# On database server (80.95.207.42)
sudo nano /etc/postgresql/*/main/postgresql.conf
```

Add or modify:
```
listen_addresses = 'localhost,80.95.207.42'
```

### 2. Configure Client Authentication
Edit pg_hba.conf to allow connections from new server:

```bash
sudo nano /etc/postgresql/*/main/pg_hba.conf
```

Add this line:
```
host    vanrentalsnewdb    epc_user    80.95.207.45/32    md5
```

### 3. Create Database (if not exists)
```bash
sudo -u postgres psql
CREATE DATABASE vanrentalsnewdb OWNER epc_user;
GRANT ALL PRIVILEGES ON DATABASE vanrentalsnewdb TO epc_user;
\q
```

### 4. Restart PostgreSQL
```bash
sudo systemctl restart postgresql
```

### 5. Test Connection from New Server
```bash
# From new server (80.95.207.45)
psql -h 80.95.207.42 -U epc_user -d vanrentalsnewdb
```

## Firewall Configuration

### On Database Server (80.95.207.42)
```bash
# Allow PostgreSQL from new server
sudo ufw allow from 80.95.207.45 to any port 5432
```

### On New Server (80.95.207.45)
```bash
# Allow outbound connections to database
sudo ufw allow out 5432
```

## Migration Notes
- The new server will connect to a separate database
- You may need to run migrations: `python manage.py migrate`
- Consider copying data if needed: `pg_dump` and `pg_restore`