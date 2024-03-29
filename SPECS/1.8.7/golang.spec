# build ids are not currently generated:
# https://code.google.com/p/go/issues/detail?id=5238
#
# also, debuginfo extraction currently fails with
# "Failed to write file: invalid section alignment"
%global debug_package %{nil}

# we are shipping the full contents of src in the data subpackage, which
# contains binary-like things (ELF data for tests, etc)
%global _binaries_in_noarch_packages_terminate_build 0

# Do not check any files in doc or src for requires
%global __requires_exclude_from ^(%{_datadir}|/usr/lib)/%{name}/(doc|src)/.*$

# Don't alter timestamps of especially the .a files (or else go will rebuild later)
# Actually, don't strip at all since we are not even building debug packages and this corrupts the dwarf testdata
%global __strip /bin/true

# rpmbuild magic to keep from having meta dependency on libc.so.6
%define _use_internal_dependency_generator 0
%define __find_requires %{nil}
%global __spec_install_post /usr/lib/rpm/check-rpaths   /usr/lib/rpm/check-buildroot  \
  /usr/lib/rpm/brp-compress

# allow turning this off
%{!?build_xemacs:%global build_xemacs 1}

# let this match the macros in macros.golang
%global goroot          /usr/lib/%{name}
%global gopath          %{_datadir}/gocode
%global go_arches       %{ix86} x86_64 %{arm} aarch64
%global golibdir        %{_libdir}/golang
%ifarch x86_64
%global gohostarch  amd64
%endif
%ifarch %{ix86}
%global gohostarch  386
%endif
%ifarch %{arm}
%global gohostarch  arm
%endif
%ifarch aarch64
%global gohostarch  arm64
%endif

%global go_api MAJOR_MINOR
%global go_version MAJOR_MINOR_PATCH

Name:           golang
Version:        MAJOR_MINOR_PATCH
Release:        0%{?dist}
Summary:        The Go Programming Language
# source tree includes several copies of Mark.Twain-Tom.Sawyer.txt under Public Domain
License:        BSD and Public Domain
URL:            http://golang.org/
Source0:        https://storage.googleapis.com/golang/go%{go_version}.src.tar.gz

# go1.5 bootstrapping. The compiler is written in golang.
BuildRequires:  golang > 1.4
BuildRequires:  pcre-devel, glibc-static, perl
%if 0%{?rhel} > 6 || 0%{?fedora} > 0
BuildRequires:  hostname
%else
BuildRequires:  net-tools
%endif

Provides:       go = %{version}-%{release}
Provides:       go-srpm-macros
Requires:       %{name}-bin
Requires:       %{name}-src = %{version}-%{release}

Patch0:         golang-1.2-verbose-build.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=1038683
#Patch1:         golang-1.8beta2-remove-ECC-p224.patch

# use the arch dependent path in the bootstrap
Patch212:       golang-1.5-bootstrap-binary-path.patch

# disable TestGdbPython
# https://github.com/golang/go/issues/11214
#Patch213:       go1.5beta1-disable-TestGdbPython.patch

# we had been just removing the zoneinfo.zip, but that caused tests to fail for users that 
# later run `go test -a std`. This makes it only use the zoneinfo.zip where needed in tests.
Patch215:       ./go1.5-zoneinfo_testing_only.patch

#PPC64X relocation overflow fix
#Patch216: ppc64x-overflow-1.patch
#Patch217: ppc64x-overflow-2.patch

# Fix for https://github.com/golang/go/issues/17276
#Patch218: tzdata-fix.patch

# Fix for https://github.com/golang/go/issues/20007
Patch219:       go-1.8-vet-perl-5.26.patch

# Having documentation separate was broken
Obsoletes:      %{name}-docs < 1.1-4

# RPM can't handle symlink -> dir with subpackages, so merge back
Obsoletes:      %{name}-data < 1.1.1-4

# go1.4 deprecates a few packages
Obsoletes:      %{name}-vim < 1.4
Obsoletes:      emacs-%{name} < 1.4

# These are the only RHEL/Fedora architectures that we compile this package for
ExclusiveArch:  %{go_arches}

Source100:      golang-gdbinit
Source101:      golang-prelink.conf
Source102:      macros.golang

%description
%{summary}.

%package       docs
Summary:       Golang compiler docs
Requires:      %{name} = %{version}-%{release}
BuildArch:     noarch
Obsoletes:     %{name}-docs < 1.1-4

%description   docs
%{summary}.

%package       misc
Summary:       Golang compiler miscellaneous sources
Requires:      %{name} = %{version}-%{release}
BuildArch:     noarch

%description   misc
%{summary}.

%package       tests
Summary:       Golang compiler tests for stdlib
Requires:      %{name} = %{version}-%{release}
BuildArch:     noarch

%description   tests
%{summary}.

%package        src
Summary:        Golang compiler source tree
BuildArch:      noarch
%description    src
%{summary}

%package        bin
Summary:        Golang core compiler tools
Requires:       go = %{version}-%{release}
# Pre-go1.5, all arches had to be bootstrapped individually, before usable, and
# env variables to compile for the target os-arch.
# Now the host compiler needs only the GOOS and GOARCH environment variables
# set to compile for the target os-arch.
Obsoletes:      %{name}-pkg-bin-linux-386 < 1.4.99
Obsoletes:      %{name}-pkg-bin-linux-amd64 < 1.4.99
Obsoletes:      %{name}-pkg-bin-linux-arm < 1.4.99
Obsoletes:      %{name}-pkg-linux-386 < 1.4.99
Obsoletes:      %{name}-pkg-linux-amd64 < 1.4.99
Obsoletes:      %{name}-pkg-linux-arm < 1.4.99
Obsoletes:      %{name}-pkg-darwin-386 < 1.4.99
Obsoletes:      %{name}-pkg-darwin-amd64 < 1.4.99
Obsoletes:      %{name}-pkg-windows-386 < 1.4.99
Obsoletes:      %{name}-pkg-windows-amd64 < 1.4.99
Obsoletes:      %{name}-pkg-plan9-386 < 1.4.99
Obsoletes:      %{name}-pkg-plan9-amd64 < 1.4.99
Obsoletes:      %{name}-pkg-freebsd-386 < 1.4.99
Obsoletes:      %{name}-pkg-freebsd-amd64 < 1.4.99
Obsoletes:      %{name}-pkg-freebsd-arm < 1.4.99
Obsoletes:      %{name}-pkg-netbsd-386 < 1.4.99
Obsoletes:      %{name}-pkg-netbsd-amd64 < 1.4.99
Obsoletes:      %{name}-pkg-netbsd-arm < 1.4.99
Obsoletes:      %{name}-pkg-openbsd-386 < 1.4.99
Obsoletes:      %{name}-pkg-openbsd-amd64 < 1.4.99

Obsoletes:      golang-vet < 0-12.1
Obsoletes:      golang-cover < 0-12.1

Requires(post): %{_sbindir}/update-alternatives
Requires(postun): %{_sbindir}/update-alternatives

# We strip the meta dependency, but go does require glibc.
# This is an odd issue, still looking for a better fix.
Requires:       glibc
Requires:       gcc
%description    bin
%{summary}

# Workaround old RPM bug of symlink-replaced-with-dir failure
%pretrans -p <lua>
for _,d in pairs({"api", "doc", "include", "lib", "src"}) do
  path = "%{goroot}/" .. d
  if posix.stat(path, "type") == "link" then
    os.remove(path)
    posix.mkdir(path)
  end
end

%ifarch x86_64
%package        shared
Summary:        Golang shared object libraries

%description    shared
%{summary}.
%endif

%prep
%setup -q -n go

# increase verbosity of build
%patch0 -p1 -b .verbose

# remove the P224 curve
#%patch1 -p1

# use the arch dependent path in the bootstrap
#%patch212 -p1 -b .bootstrap

# disable TestGdbPython
#%patch213 -p1 -b .gdb

%patch215 -p1

#%patch216 -p1
#%patch217 -p1

#%patch218 -p1

%patch219 -p1

%build
# print out system information
uname -a
cat /proc/cpuinfo
cat /proc/meminfo

# go1.5 bootstrapping. The compiler is written in golang.
export GOROOT_BOOTSTRAP=%{goroot}

# set up final install location
export GOROOT_FINAL=%{goroot}

# TODO use the system linker to get the system link flags and build-id
# when https://code.google.com/p/go/issues/detail?id=5221 is solved
#export GO_LDFLAGS="-linkmode external -extldflags $RPM_LD_FLAGS"

export GOHOSTOS=linux
export GOHOSTARCH=%{gohostarch}

pushd src

# use our gcc options for this build, but store gcc as default for compiler
# DEBUG TEST
#CFLAGS="$RPM_OPT_FLAGS" \
#LDFLAGS="$RPM_LD_FLAGS" \
#CC="gcc" \
#CC_FOR_TARGET="gcc" \
#GOOS=linux \
#GOARCH=%{gohostarch} \
	./make.bash --no-clean
popd

%ifarch x86_64
# TODO get linux/386 support for shared objects.
# golang shared objects for stdlib
GOROOT=$(pwd) PATH=$(pwd)/bin:$PATH go install -buildmode=shared std
%endif

%install
rm -rf $RPM_BUILD_ROOT

# create the top level directories
mkdir -p $RPM_BUILD_ROOT%{_bindir}
mkdir -p $RPM_BUILD_ROOT%{goroot}

# install everything into libdir (until symlink problems are fixed)
# https://code.google.com/p/go/issues/detail?id=5830
cp -apv api bin doc favicon.ico lib pkg robots.txt src misc test VERSION \
   $RPM_BUILD_ROOT%{goroot}

# bz1099206
find $RPM_BUILD_ROOT%{goroot}/src -exec touch -r $RPM_BUILD_ROOT%{goroot}/VERSION "{}" \;
# and level out all the built archives
touch $RPM_BUILD_ROOT%{goroot}/pkg
find $RPM_BUILD_ROOT%{goroot}/pkg -exec touch -r $RPM_BUILD_ROOT%{goroot}/pkg "{}" \;
# generate the spec file ownership of this source tree and packages
cwd=$(pwd)
src_list=$cwd/go-src.list
pkg_list=$cwd/go-pkg.list
shared_list=$cwd/go-shared.list
misc_list=$cwd/go-misc.list
docs_list=$cwd/go-docs.list
tests_list=$cwd/go-tests.list
rm -f $src_list $pkg_list $docs_list $misc_list $tests_list $shared_list
touch $src_list $pkg_list $docs_list $misc_list $tests_list $shared_list
pushd $RPM_BUILD_ROOT%{goroot}
	find src/ -type d -a \( ! -name testdata -a ! -ipath '*/testdata/*' \) -printf '%%%dir %{goroot}/%p\n' >> $src_list
	find src/ ! -type d -a \( ! -ipath '*/testdata/*' -a ! -name '*_test.go' \) -printf '%{goroot}/%p\n' >> $src_list

	find bin/ pkg/ -type d -a ! -path '*_dynlink/*' -printf '%%%dir %{goroot}/%p\n' >> $pkg_list
	find bin/ pkg/ ! -type d -a ! -path '*_dynlink/*' -printf '%{goroot}/%p\n' >> $pkg_list

	find doc/ -type d -printf '%%%dir %{goroot}/%p\n' >> $docs_list
	find doc/ ! -type d -printf '%{goroot}/%p\n' >> $docs_list

	find misc/ -type d -printf '%%%dir %{goroot}/%p\n' >> $misc_list
	find misc/ ! -type d -printf '%{goroot}/%p\n' >> $misc_list

%ifarch x86_64
    mkdir -p %{buildroot}/%{_libdir}/
    mkdir -p %{buildroot}/%{golibdir}/
    for file in $(find .  -iname "*.so" ); do
        chmod 755 $file
        mv  $file %{buildroot}/%{golibdir}
        pushd $(dirname $file)
        ln -fs %{golibdir}/$(basename $file) $(basename $file)
        popd
        echo "%%{goroot}/$file" >> $shared_list
        echo "%%{golibdir}/$(basename $file)" >> $shared_list
    done
    
	find pkg/*_dynlink/ -type d -printf '%%%dir %{goroot}/%p\n' >> $shared_list
	find pkg/*_dynlink/ ! -type d -printf '%{goroot}/%p\n' >> $shared_list
%endif

	find test/ -type d -printf '%%%dir %{goroot}/%p\n' >> $tests_list
	find test/ ! -type d -printf '%{goroot}/%p\n' >> $tests_list
	find src/ -type d -a \( -name testdata -o -ipath '*/testdata/*' \) -printf '%%%dir %{goroot}/%p\n' >> $tests_list
	find src/ ! -type d -a \( -ipath '*/testdata/*' -o -name '*_test.go' \) -printf '%{goroot}/%p\n' >> $tests_list
	# this is only the zoneinfo.zip
	find lib/ -type d -printf '%%%dir %{goroot}/%p\n' >> $tests_list
	find lib/ ! -type d -printf '%{goroot}/%p\n' >> $tests_list
popd

# remove the doc Makefile
rm -rfv $RPM_BUILD_ROOT%{goroot}/doc/Makefile

# put binaries to bindir, linked to the arch we're building,
# leave the arch independent pieces in {goroot}
mkdir -p $RPM_BUILD_ROOT%{goroot}/bin/linux_%{gohostarch}
ln -sf %{goroot}/bin/go $RPM_BUILD_ROOT%{goroot}/bin/linux_%{gohostarch}/go
ln -sf %{goroot}/bin/gofmt $RPM_BUILD_ROOT%{goroot}/bin/linux_%{gohostarch}/gofmt

# ensure these exist and are owned
mkdir -p $RPM_BUILD_ROOT%{gopath}/src/github.com
mkdir -p $RPM_BUILD_ROOT%{gopath}/src/bitbucket.org
mkdir -p $RPM_BUILD_ROOT%{gopath}/src/code.google.com/p
mkdir -p $RPM_BUILD_ROOT%{gopath}/src/golang.org/x

# make sure these files exist and point to alternatives
rm -f $RPM_BUILD_ROOT%{_bindir}/go
ln -sf /etc/alternatives/go $RPM_BUILD_ROOT%{_bindir}/go
rm -f $RPM_BUILD_ROOT%{_bindir}/gofmt
ln -sf /etc/alternatives/gofmt $RPM_BUILD_ROOT%{_bindir}/gofmt

# gdbinit
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/gdbinit.d
cp -av %{SOURCE100} $RPM_BUILD_ROOT%{_sysconfdir}/gdbinit.d/golang.gdb

# prelink blacklist
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/prelink.conf.d
cp -av %{SOURCE101} $RPM_BUILD_ROOT%{_sysconfdir}/prelink.conf.d/golang.conf

# rpm macros
mkdir -p %{buildroot}
%if 0%{?rhel} > 6 || 0%{?fedora} > 0
mkdir -p $RPM_BUILD_ROOT%{_rpmconfigdir}/macros.d
cp -av %{SOURCE102} $RPM_BUILD_ROOT%{_rpmconfigdir}/macros.d/macros.golang
%else
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/rpm
cp -av %{SOURCE102} $RPM_BUILD_ROOT%{_sysconfdir}/rpm/macros.golang
%endif


%check
export GOROOT=$(pwd -P)
export PATH="$GOROOT"/bin:"$PATH"
cd src

export CC="gcc"
export CFLAGS="$RPM_OPT_FLAGS"
export LDFLAGS="$RPM_LD_FLAGS"

# make sure to not timeout
export GO_TEST_TIMEOUT_SCALE=2

./run.bash --no-rebuild -v -v -v -k
cd ..


%post bin
%{_sbindir}/update-alternatives --install %{_bindir}/go \
	go %{goroot}/bin/go 90 \
	--slave %{_bindir}/gofmt gofmt %{goroot}/bin/gofmt

%preun bin
if [ $1 = 0 ]; then
	%{_sbindir}/update-alternatives --remove go %{goroot}/bin/go
fi


%files
%doc AUTHORS CONTRIBUTORS LICENSE PATENTS
# VERSION has to be present in the GOROOT, for `go install std` to work
%doc %{goroot}/VERSION
%dir %{goroot}/doc
%doc %{goroot}/doc/*

# go files
%dir %{goroot}
%exclude %{goroot}/bin/
%exclude %{goroot}/pkg/
%exclude %{goroot}/src/
%exclude %{goroot}/doc/
%exclude %{goroot}/misc/
%{goroot}/*

# ensure directory ownership, so they are cleaned up if empty
%dir %{gopath}
%dir %{gopath}/src
%dir %{gopath}/src/github.com/
%dir %{gopath}/src/bitbucket.org/
%dir %{gopath}/src/code.google.com/
%dir %{gopath}/src/code.google.com/p/
%dir %{gopath}/src/golang.org
%dir %{gopath}/src/golang.org/x


# gdbinit (for gdb debugging)
%{_sysconfdir}/gdbinit.d

# prelink blacklist
%{_sysconfdir}/prelink.conf.d

%if 0%{?rhel} > 6 || 0%{?fedora} > 0
%{_rpmconfigdir}/macros.d/macros.golang
%else
%{_sysconfdir}/rpm/macros.golang
%endif


%files -f go-src.list src

%files -f go-docs.list docs

%files -f go-misc.list misc

%files -f go-tests.list tests

%files -f go-pkg.list bin
%{_bindir}/go
%{_bindir}/gofmt

%ifarch x86_64
%files -f go-shared.list shared
%endif

%changelog
* Mon Dec 05 2016 Jakub Čajka <jcajka@fedoraproject.org> - 1.7.4-1
- Bump to 1.7.4
- Resolves: BZ#1400732

* Fri Nov 18 2016 Jakub Čajka <jcajka@fedoraproject.org> - 1.7.3-2
- enable back p224 curve(see BZ#1038683)

* Fri Oct 21 2016 Jakub Čajka <jcajka@fedoraproject.org> - 1.7.3-1
- rebase to go1.7.3
- Fix possible relocation overflows on ppc
- Fix failing test due to latest tzdata

* Fri Sep 16 2016 Jakub Čajka <jcajka@fedoraproject.org> - 1.7.1-1
- rebase to go1.7.1
- Resolves: BZ#1293449 - CVE-2015-8618, BZ#1357601 - CVE-2016-5386,
BZ#1324345 - CVE-2016-3959, BZ#1376555

* Mon Oct 19 2015 Vincent Batts <vbatts@fedoraproject.org> - 1.5.1-1
- bz1271709 include patch from upstream fix

* Wed Sep 09 2015 Vincent Batts <vbatts@fedoraproject.org> - 1.5.1-0
- update to go1.5.1

* Thu Aug 27 2015 Vincent Batts <vbatts@fedoraproject.org> - 1.5-6
- starting a shared object subpackage. This will be x86_64 only until upstream supports more arches shared objects.

* Thu Aug 27 2015 Vincent Batts <vbatts@fedoraproject.org> - 1.5-5
- bz991759 gdb path fix

* Wed Aug 26 2015 Vincent Batts <vbatts@fedoraproject.org> - 1.5-4
- disable shared object until linux/386 is ironned out
- including the test/ directory for tests

* Tue Aug 25 2015 Vincent Batts <vbatts@fedoraproject.org> - 1.5-3
- bz1256910 only allow the golang zoneinfo.zip to be used in tests
- bz1166611 add golang.org/x directory
- bz1256525 include stdlib shared object. This will let other libraries and binaries
  build with `go build -buildmode=shared -linkshared ...` or similar.

* Sun Aug 23 2015 Peter Robinson <pbrobinson@fedoraproject.org> 1.5-2
- Enable aarch64
- Minor cleanups

* Thu Aug 20 2015 Vincent Batts <vbatts@fedoraproject.org> - 1.5-1
- updating to go1.5

* Wed Aug 05 2015 Vincent Batts <vbatts@fedoraproject.org> - 1.4.2-3
- bz1250352

* Wed Mar 18 2015 Vincent Batts <vbatts@fedoraproject.org> - 1.4.2-2
- obsoleting deprecated packages

* Wed Feb 18 2015 Vincent Batts <vbatts@fedoraproject.org> - 1.4.2-1
- updating to go1.4.2

* Fri Jan 16 2015 Vincent Batts <vbatts@fedoraproject.org> - 1.4.1-1
- updating to go1.4.1

* Fri Jan 02 2015 Vincent Batts <vbatts@fedoraproject.org> - 1.4-2
- doc organizing

* Thu Dec 11 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.4-1
- update to go1.4 release

* Wed Dec 03 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3.99-3.1.4rc2
- update to go1.4rc2

* Mon Nov 17 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3.99-2.1.4rc1
- update to go1.4rc1

* Thu Oct 30 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3.99-1.1.4beta1
- update to go1.4beta1

* Thu Oct 30 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3.3-3
- macros will need to be in their own rpm

* Fri Oct 24 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3.3-2
- split out rpm macros (bz1156129)
- progress on gccgo accomodation

* Wed Oct 01 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3.3-1
- update to go1.3.3 (bz1146882)

* Mon Sep 29 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3.2-1
- update to go1.3.2 (bz1147324)

* Wed Aug 13 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.2.2-22
- more work to get cgo.a timestamps to line up, due to build-env

* Wed Aug 13 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.2.2-21
- touch cgo.a regardless

* Wed Aug 13 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.2.2-20
- rpm dependency ordering for %%post

* Tue Aug 12 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.2.2-19
- finally check for a Stale cgo in a %%post

* Tue Aug 12 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.2.2-18
- explicitly list all the files and directories for the packages trees

* Tue Aug 12 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.2.2-17
- explicitly list all the files and directories of the src tree, to preserve timestamps

* Mon Aug 11 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.2.2-16
- touch all the built archives to be the same

* Mon Aug 11 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.2.2-15
- make golang-src 'noarch' again, since that was not a fix, and takes up more space

* Mon Aug 11 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.2.2-14
- update timestamps of source files during %%install bz1099206

* Fri Aug 08 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.2.2-13
- update timestamps of source during %%install bz1099206

* Fri Aug 08 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.2.2-12
- set another version constraint on xemacs due to bz1127518

* Wed Aug 06 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.2.2-11
- set a version constraint on xemacs due to bz1127518

* Wed Aug 06 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.2.2-10
- make the source subpackage arch'ed, instead of noarch

* Tue Jul 15 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.2.2-9
- fix the loading of gdb safe-path. bz981356

* Tue Jul 08 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.2.2-8
- `go install std` requires gcc, to build cgo. bz1105901, bz1101508

* Wed May 21 2014 Vincent Batts <vbatts@redhat.com> 1.2.2-7
- bz1099206 ghost files are not what is needed

* Tue May 20 2014 Vincent Batts <vbatts@redhat.com> 1.2.2-6
- bz1099206 more fixing. The packages %%post need golang-bin present first

* Tue May 20 2014 Vincent Batts <vbatts@redhat.com> 1.2.2-5
- bz1099206 more fixing. Let go fix its own timestamps and freshness

* Tue May 20 2014 Vincent Batts <vbatts@redhat.com> 1.2.2-4
- fix the existence and alternatives of `go` and `gofmt`

* Mon May 19 2014 Vincent Batts <vbatts@redhat.com> 1.2.2-3
- bz1099206 fix timestamp issue caused by koji builders

* Fri May 09 2014 Vincent Batts <vbatts@redhat.com> 1.2.2-2
- more arch file shuffling

* Fri May 09 2014 Vincent Batts <vbatts@redhat.com> 1.2.2-1
- update to go1.2.2

* Thu May 08 2014 Vincent Batts <vbatts@redhat.com> 1.2.1-8
- RHEL6 rpm macros can't %%exlude missing files

* Wed May 07 2014 Vincent Batts <vbatts@redhat.com> 1.2.1-7
- missed two arch-dependent src files

* Wed May 07 2014 Vincent Batts <vbatts@redhat.com> 1.2.1-6
- put generated arch-dependent src in their respective RPMs

* Fri Apr 11 2014 Vincent Batts <vbatts@redhat.com> 1.2.1-5
- skip test that is causing a SIGABRT on fc21 bz1086900

* Thu Apr 10 2014 Vincent Batts <vbatts@fedoraproject.org> 1.2.1-4
- fixing file and directory ownership bz1010713

* Wed Apr 09 2014 Vincent Batts <vbatts@fedoraproject.org> 1.2.1-3
- including more to macros (%%go_arches)
- set a standard goroot as /usr/lib/golang, regardless of arch
- include sub-packages for compiler toolchains, for all golang supported architectures

* Wed Mar 26 2014 Vincent Batts <vbatts@fedoraproject.org> 1.2.1-2
- provide a system rpm macros. Starting with %gopath

* Tue Mar 04 2014 Adam Miller <maxamillion@fedoraproject.org> 1.2.1-1
- Update to latest upstream

* Thu Feb 20 2014 Adam Miller <maxamillion@fedoraproject.org> 1.2-7
- Remove  _BSD_SOURCE and _SVID_SOURCE, they are deprecated in recent
  versions of glibc and aren't needed

* Wed Feb 19 2014 Adam Miller <maxamillion@fedoraproject.org> 1.2-6
- pull in upstream archive/tar implementation that supports xattr for
  docker 0.8.1

* Tue Feb 18 2014 Vincent Batts <vbatts@redhat.com> 1.2-5
- provide 'go', so users can yum install 'go'

* Fri Jan 24 2014 Vincent Batts <vbatts@redhat.com> 1.2-4
- skip a flaky test that is sporadically failing on the build server

* Thu Jan 16 2014 Vincent Batts <vbatts@redhat.com> 1.2-3
- remove golang-godoc dependency. cyclic dependency on compiling godoc

* Wed Dec 18 2013 Vincent Batts <vbatts@redhat.com> - 1.2-2
- removing P224 ECC curve

* Mon Dec 2 2013 Vincent Batts <vbatts@fedoraproject.org> - 1.2-1
- Update to upstream 1.2 release
- remove the pax tar patches

* Tue Nov 26 2013 Vincent Batts <vbatts@redhat.com> - 1.1.2-8
- fix the rpmspec conditional for rhel and fedora

* Thu Nov 21 2013 Vincent Batts <vbatts@redhat.com> - 1.1.2-7
- patch tests for testing on rawhide
- let the same spec work for rhel and fedora

* Wed Nov 20 2013 Vincent Batts <vbatts@redhat.com> - 1.1.2-6
- don't symlink /usr/bin out to ../lib..., move the file
- seperate out godoc, to accomodate the go.tools godoc

* Fri Sep 20 2013 Adam Miller <maxamillion@fedoraproject.org> - 1.1.2-5
- Pull upstream patches for BZ#1010271
- Add glibc requirement that got dropped because of meta dep fix

* Thu Sep 19 2013 Adam Miller <maxamillion@fedoraproject.org> - 1.2.2-3
- fix the libc meta dependency (thanks to vbatts [at] redhat.com for the fix)

* Fri Aug 16 2013 Adam Miller <admiller@redhat.com> - 1.1.2-2
- vim-filesystem only required for Fedora , vim-common owns those files in RHEL

* Fri Aug 16 2013 Adam Miller <admiller@redhat.com> - 1.1.2-1
- Update to latest upstream

* Fri Aug 16 2013 Adam Miller <admiller@redhat.com> - 1.1.1-6
- Remove xemacs bits for RHEL build

* Wed Jul 10 2013 Adam Goode <adam@spicenitz.org> - 1.1.1-5
- Blacklist testdata files from prelink
- Again try to fix #973842

* Fri Jul  5 2013 Adam Goode <adam@spicenitz.org> - 1.1.1-4
- Move src to libdir for now (#973842) (upstream issue https://code.google.com/p/go/issues/detail?id=5830)
- Eliminate noarch data package to work around RPM bug (#975909)
- Try to add runtime-gdb.py to the gdb safe-path (#981356)

* Wed Jun 19 2013 Adam Goode <adam@spicenitz.org> - 1.1.1-3
- Use lua for pretrans (http://fedoraproject.org/wiki/Packaging:Guidelines#The_.25pretrans_scriptlet)

* Mon Jun 17 2013 Adam Goode <adam@spicenitz.org> - 1.1.1-2
- Hopefully really fix #973842
- Fix update from pre-1.1.1 (#974840)

* Thu Jun 13 2013 Adam Goode <adam@spicenitz.org> - 1.1.1-1
- Update to 1.1.1
- Fix basically useless package (#973842)

* Sat May 25 2013 Dan Horák <dan[at]danny.cz> - 1.1-3
- set ExclusiveArch

* Fri May 24 2013 Adam Goode <adam@spicenitz.org> - 1.1-2
- Fix noarch package discrepancies

* Fri May 24 2013 Adam Goode <adam@spicenitz.org> - 1.1-1
- Initial Fedora release.
- Update to 1.1

* Thu May  9 2013 Adam Goode <adam@spicenitz.org> - 1.1-0.3.rc3
- Update to rc3

* Thu Apr 11 2013 Adam Goode <adam@spicenitz.org> - 1.1-0.2.beta2
- Update to beta2

* Tue Apr  9 2013 Adam Goode <adam@spicenitz.org> - 1.1-0.1.beta1
- Initial packaging.
