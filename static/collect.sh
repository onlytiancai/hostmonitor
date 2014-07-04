URL='http://hostmonitor.ihuhao.com/api/collect'
if [ ! -n "$1" ] ;then
    echo "you have not input the email !"
    exit 1
fi

curl ${URL} -d uptime_info="`uptime`" \
    -d df_info="`df -h`" \
    -d free_info="`free -m`" \
    -d email="$1" \
    -d hostname="`hostname`" \
    -d mac_addr="`cat /sys/class/net/eth0/address`"
