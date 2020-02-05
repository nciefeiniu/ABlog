#!/bin/bash
export PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# ====================================================
# Description:Ablog一键脚本 for Debian 8+ 、CentOS 7、Ubuntu 16+
# ====================================================

#fonts color
Red="\033[31m"
Font="\033[0m"
Blue="\033[36m"
cur_path=`pwd`

#root permission
check_root(){
    if [[ $EUID -ne 0 ]]; then
    echo "${Red}Error:请使用root运行该脚本！"${Font} 1>&2
    exit 1
    fi
}

#check system
check_system(){
    if [[ -f /etc/redhat-release ]]; then
        release="centos"
    elif cat /etc/issue | grep -Eqi "debian"; then
        release="debian"
    elif cat /etc/issue | grep -Eqi "ubuntu"; then
        release="ubuntu"
    elif cat /etc/issue | grep -Eqi "centos|red hat|redhat"; then
        release="centos"
    elif cat /proc/version | grep -Eqi "debian"; then
        release="debian"
    elif cat /proc/version | grep -Eqi "ubuntu"; then
        release="ubuntu"
    elif cat /proc/version | grep -Eqi "centos|red hat|redhat"; then
        release="centos"
    fi
}

#check version
check_version(){
    if [[ -s /etc/redhat-release ]]; then
     version=`cat /etc/redhat-release|sed -r 's/.* ([0-9]+)\..*/\1/'`
    else
     version=`grep -oE  "[0-9.]+" /etc/issue | cut -d . -f 1`
    fi
    bit=`uname -m`
    if [[ ${bit} = "x86_64" ]]; then
        bit="64"
    else
        bit="32"
    fi
    if [[ "${release}" = "centos" && ${version} -ge 7 ]];then
        echo -e "${Blue}当前系统为CentOS ${version}${Font} "
    elif [[ "${release}" = "debian" && ${version} -ge 8 ]];then
        echo -e "${Blue}当前系统为Debian ${version}${Font} "
    elif [[ "${release}" = "ubuntu" && ${version} -ge 16 ]];then
        echo -e "${Blue}当前系统为Ubuntu ${version}${Font} "
    else
        echo -e "${Red}脚本不支持当前系统，安装中断!${Font} "
        exit 1
    fi
    for EXE in grep cut xargs systemctl ip awk
    do
        if ! type -p ${EXE}; then
            echo -e "${Red}系统精简厉害，脚本自动退出${Font}"
            exit 1
        fi
    done
}

install_pyenv(){
    s=`ls -a $HOME/ | grep ".pyenv" | wc -l`
    if [[ $s = 0 ]]; then
        echo -e "${Blue}正在安装pyenv！${Font}"
        if [[ "${release}" = "centos" ]]; then
            yum install git
            yum install curl -y
            yum -y install zlib\*
            yum install gcc -y
            yum install make -y
            yum install openssl -y
            yum install openssl-devel -y
            yum install sqlite-devel -y
            yum install libffi-devel -y
            yum install readline readline-devel -y
        else
            apt-get install -y git
            apt-get install -y curl
            apt-get install -y gcc
            apt-get install -y make
            apt-get install -y zlib1g
            apt-get install -y zlib1g-dev
            apt-get install -y zlibc
            apt-get install -y libffi-devel
            apt-get install -y libffi-dev
            apt-get install -y libssl-dev
            apt-get install -y sqlite3
            apt-get install -y libsqlite3-dev
            apt-get install -y libreadline6
            apt-get install -y libreadline6–dev
        fi
        curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash
        echo "export PATH=\"\$HOME/.pyenv/bin:\$PATH\"
eval \"\$(pyenv init -)\"
eval \"\$(pyenv virtualenv-init -)\"" >> ~/.bashrc

        source ~/.bashrc

        s=`ls -a $HOME/ | grep ".pyenv" | wc -l`
        if [[ $s = 0 ]]; then
            echo -e "${Red}安装pyenv出错！请先按照：https://www.abbeyok.com/archives/352 安装pyenv${Font}"
            exit 1
        else
            echo "pyenv安装完成"
        fi
    else
        echo "pyenv已安装"
    fi

}

install_py374(){
    $HOME/.pyenv/bin/pyenv install -v 3.7.4
    $HOME/.pyenv/bin/pyenv rehash
    $HOME/.pyenv/bin/pyenv local 3.7.4
}



config_file(){
    cur_dir=`pwd`
    cp config.py.sample config.py
    cp wp_to_blog.py.sample wp_to_blog.py
}


#enter info
enter_info(){
    echo -e "${Blue}设置用户信息！${Font}"
    echo "请设置[数据储存]方式:"
    echo "1. mysql"
    echo "2. sqlite"
    stty erase '^H' && read -p " 请输入数字 [1-2]:" store_num

    case "$store_num" in
        1)
        STORE_METHOD='mysql'

        read -p "请设置MySQL用户名:" MYSQL_USER
        sed -i "s/MYSQL_USER = 'mysql_user'/MYSQL_USER = '${MYSQL_USER}'/g" config.py

        read -p "请设置数据储存方式[mysql/sqlite]:" MYSQL_USER
        sed -i "s/MYSQL_USER = 'mysql_user'/MYSQL_USER = '${MYSQL_USER}'/g" config.py

        read -p "请设置MySQL密码:" MYSQL_PASSWORD
        sed -i "s/MYSQL_PASSWORD = 'mysql_passwd'/MYSQL_PASSWORD = '${MYSQL_PASSWORD}'/g" config.py

        read -p "请设置MySQL数据库名:" MYSQL_DB
        sed -i "s/MYSQL_DB = 'MYSQL_DATABASE_CHARSET'/MYSQL_DB = '${MYSQL_DB}'/g" config.py

        ;;
        2)
        STORE_METHOD='sqlite'
        sed -i "s/STORE_METHOD='mysql'/STORE_METHOD='sqlite'/g" config.py
        ;;
        *)
        clear
        echo -e "${Error}:请输入正确数字 [1-2]"
        ;;
    esac


    echo "请设置[数据缓存]方式:"
    echo "1. redis"
    echo "2. simple"
    stty erase '^H' && read -p " 请输入数字 [1-2]:" cache_num

    case "$cache_num" in
        1)
        echo
        ;;
        2)
        sed -i "s/CACHE_TYPE = 'redis'/CACHE_TYPE = 'simple'/g" config.py
        ;;
        *)
        clear
        echo -e "${Error}:请输入正确数字 [1-2]"
        ;;
    esac

    read -p "请设置管理员账号:" ADMIN_NAME
    sed -i "s/ADMIN_NAME = 'Abbey'/ADMIN_NAME = '${ADMIN_NAME}'/g" config.py

    read -p "请设置管理员邮箱:" ADMIN_MAIL
    sed -i "s/ADMIN_MAIL = 'abbeyok@gmail.com'/ADMIN_MAIL = '${ADMIN_MAIL}'/g" config.py

    read -p "请设置管理员密码:" ADMIN_PASSWORD
    sed -i "s/ADMIN_PASSWORD = 'Admin'/ADMIN_PASSWORD = '${ADMIN_PASSWORD}'/g" config.py

    read -p "请设置管理员简介:" ADMIN_PROFILE
    sed -i "s/ADMIN_PROFILE = '数据分析兼职Python开发'/ADMIN_PROFILE = '${ADMIN_PROFILE}'/g" config.py

    read -p "请设置网站名称:" SITE_NAME
    sed -i "s/SITE_NAME = '一个人的公交'/SITE_NAME = '${SITE_NAME}'/g" config.py

    read -p "请设置网站标题:" SITE_TITLE
    sed -i "s/SITE_TITLE = 'My Blog'/SITE_TITLE = '${SITE_TITLE}'/g" config.py

    read -p "请设置网站协议[http/https]:" WEB_PROTOCOL
    sed -i "s/WEB_PROTOCOL = 'https'/WEB_PROTOCOL = '${WEB_PROTOCOL}'/g" config.py

    read -p "请设置网站域名[www.abbeyok.com]:" WEB_URL
    sed -i "s/WEB_URL = 'www.abbeyok.com'/WEB_URL = '${WEB_URL}'/g" config.py

    echo "是否设置payjs账号信息？:"
    echo "1. 设置"
    echo "2. 不设置"
    stty erase '^H' && read -p " 请输入数字 [1-2]:" pay_num

    case "$pay_num" in
        1)
        read -p "请设置payjs商户号:" PAYJS_MCHID
        sed -i "s/PAYJS_MCHID=''/PAYJS_MCHID='${PAYJS_MCHID}'/g" config.py

        read -p "请设置payjs密钥:" PAYJS_KEY
        sed -i "s/PAYJS_KEY=''/PAYJS_KEY='${PAYJS_KEY}'/g" config.py
        ;;
        2)
        echo -e "${Blue}:后续可自行在config.py设置payjs账号信息${Font}"
        ;;
        *)
        echo -e "${Blue}:后续可自行在config.py设置payjs账号信息${Font}"
        ;;
    esac

}



install_package(){
    echo -e "${Blue}开始安装依赖包！${Font}"
    $HOME/.pyenv/versions/3.7.4/bin/pip install -r requirements.txt
}

init_blog(){
    echo -e "${Blue}开始初始化博客！${Font}"
    $HOME/.pyenv/versions/3.7.4/bin/python manage.py deploy
}


#set start up
start(){
    echo -e "${Blue}正在为相关应用设置开机自启！${Font}"
    echo "[Unit]
Description=blog
After=network.target
Wants=network.target

[Service]
Type=simple
PIDFile=/var/run/blog.pid
WorkingDirectory=${cur_path}
ExecStart=$HOME/.pyenv/versions/3.7.4/bin/gunicorn -keventlet -b 0.0.0.0:34567 manage:app
RestartPreventExitStatus=23
Restart=always
User=root

[Install]
WantedBy=multi-user.target
" > '/etc/systemd/system/blog.service'

        systemctl start blog
        systemctl enable blog
}

#open firewall
firewall(){
    if [[ "${release}" = "centos" ]]; then
        firewall-cmd --zone=public --add-port=34567/tcp --permanent
        firewall-cmd --reload
    else
        apt-get install -y iptables
        iptables -I INPUT -p tcp --dport 34567 -j ACCEPT
        iptables-save
    fi
}
#Complete info
info(){
    local_ip=`curl http://whatismyip.akamai.com`
    echo -e "———————————————————————————————————————"
    echo -e "${Blue}ABlog安装完成！${Font}"
    echo -e "${Blue}访问地址：http://${local_ip}:34567${Font}"
    echo -e "${Blue}后台地址：http://${local_ip}:34567/admin${Font}"
    echo -e "${Blue}绑定域名方式，请参考：https://www.showdoc.cc/pyone?page_id=2564515561537846${Font}"
    echo -e "${Blue}常用命令：${Font}"
    echo -e "${Blue}1. 暂停博客: systemctl stop blog${Font}"
    echo -e "${Blue}2. 启动博客: systemctl start blog${Font}"
    echo -e "${Blue}3. 重启博客: systemctl restart blog${Font}"
    echo -e "${Blue}4. 手动运行博客: systemctl stop pyone && gunicorn -keventlet -b 0:34567 manage:app${Font}"
    echo -e "———————————————————————————————————————"
}


#start menu
main(){
    check_root
    check_system
    check_version
    check_service
    clear
    echo -e "———————————————————————————————————————"
    echo -e "${Blue}ABlog一键脚本 for Debian 8+ 、CentOS 7、Ubuntu 16+${Font}"
    echo -e "${Blue}请提前通过宝塔安装MySQL、Redis${Font}"
    echo -e "${Blue}如果未安装MySQL和Redis，储存方式请选：sqlite，缓存方式请选：simple${Font}"
    echo -e "———————————————————————————————————————"
    install_pyenv
    install_py374
    config_file
    enter_info

    install_package
    init_blog
    start
    firewall
    info
}

main
