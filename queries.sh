sqsh -D Cubx -S 192.168.111.10 -U sa -C "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE';"

sqsh -D Cubx -S 192.168.111.10 -U sa -C "Select MITARBEITER_ID, MITARBEITER_NR, KUERZEL, NAME, VORNAME from ST_MITARBEITER;"

