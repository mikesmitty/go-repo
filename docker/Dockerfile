FROM fedora:28

RUN yum -y --setopt="tsflags=nodocs" update && \
	yum -y --setopt="tsflags=nodocs" install mock rpm-sign expect && \
	yum clean all && \
	rm -rf /var/cache/yum/

#Configure users
RUN useradd -u 1000 -G mock builder && \
	chmod g+w /etc/mock/*.cfg

VOLUME ["/rpmbuild"]

COPY mock /etc/mock

# create mock cache on external volume to speed up build
RUN install -g mock -m 2775 -d /rpmbuild/cache/mock
RUN echo "config_opts['cache_topdir'] = '/rpmbuild/cache/mock'" >> /etc/mock/site-defaults.cfg
RUN echo "config_opts['use_nspawn'] = False" >> /etc/mock/site-defaults.cfg

ADD ./build-rpm.sh /build-rpm.sh
RUN chmod +x /build-rpm.sh
#RUN setcap cap_sys_admin+ep /usr/sbin/mock
ADD ./rpm-sign.exp /rpm-sign.exp
RUN chmod +x /rpm-sign.exp

USER builder
ENV HOME /home/builder
CMD ["/build-rpm.sh"]
