#seb kort skicka mail till invoices
/usr/local/bin/pagero.py:
  file.managed:
    - source: salt://sftp/pagero.py
    - mode: 755
    - user: root
    - group: root
pagero:
  service:
    - name: pagero.timer
    - running
    - enable: True
    - require:
      - file: /etc/systemd/system/pagero.timer
      - file: /etc/systemd/system/pagero.service
/etc/systemd/system/pagero.timer:
  file.managed:
    - source: salt://sftp/pagero.timer
    - mode: 755
    - user: root
    - group: root
/etc/systemd/system/pagero.service:
  file.managed:
    - source: salt://sftp/pagero.service
    - mode: 755
    - user: root
    - group: root
