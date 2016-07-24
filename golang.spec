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
%global __spec_install_post /usr/lib/rpm/check-rpaths \
  /usr/lib/rpm/check-buildroot  \
  /usr/lib/rpm/brp-compress

# let this match the macros in macros.golang
%global goroot          /usr/lib/%{name}
%global gopath          %{_datadir}/gocode
#%global go_arches       %{ix86} x86_64 %{arm}
%global go_arches       x86_64
%ifarch x86_64
%global gohostarch  amd64
%endif
%ifarch %{ix86}
%global gohostarch  386
%endif
%ifarch %{arm}
%global gohostarch  arm
%endif

%global go_api MAJOR_MINOR

Name:           golang
Version:        MAJOR_MINOR_RELEASE
Release:        1%{?dist}
Summary:        The Go Programming Language

License:        BSD
URL:            http://golang.org/
Source0:        https://storage.googleapis.com/golang/go%{version}.src.tar.gz

# this command moved places
#%if 0%{?fedora} >= 21
#BuildRequires:  /usr/bin/hostname
#Patch210:       golang-f21-hostname.patch

# Patch211 - F21+ has glibc 2.19.90 (2.20 devel)+ which deprecates
#            _BSD_SOURCE and _SVID_SOURCE
#Patch211:       golang-1.2-BSD-SVID-SOURCE.patch
#%else
BuildRequires:  /bin/hostname
#%endif

Provides:       go = %{version}-%{release}
Requires:       golang-bin
Requires:       golang-src = %{version}-%{release}

#Patch0:         golang-1.2-verbose-build.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=1038683
#Patch1:         golang-1.2-remove-ECC-p224.patch

# https://github.com/golang/go/issues/9605
#Patch2: 	disable-flanky-CPU-profile-test.patch
# Having documentation separate was broken
Obsoletes:      %{name}-docs < 1.1-4

# RPM can't handle symlink -> dir with subpackages, so merge back
Obsoletes:      %{name}-data < 1.1.1-4

# emacs and vim subpackages no longer provided in 1.4.2
Obsoletes:      emacs-%{name} <= 1.3.3-3
Obsoletes:      %{name}-vim <= 1.3.3

# obsoletes *BSD sub packages
Obsoletes:	pkg-plan9-386 <= 1.4.2
Obsoletes:	pkg-plan9-amd64 <= 1.4.2
Obsoletes:	pkg-freebsd-386 <= 1.4.2
Obsoletes:	pkg-freebsd-amd64 <= 1.4.2
Obsoletes:	pkg-freebsd-arm <= 1.4.2
Obsoletes:	pkg-netbsd-386 <= 1.4.2
Obsoletes:	pkg-netbsd-amd64 <= 1.4.2
Obsoletes:	pkg-netbsd-arm <= 1.4.2
Obsoletes:	pkg-openbsd-386 <= 1.4.2
Obsoletes:	pkg-openbsd-amd64 <= 1.4.2

# These are the only RHEL/Fedora architectures that we compile this package for
ExclusiveArch:  %{go_arches}

Source100:      golang-gdbinit
Source101:      golang-prelink.conf
Source102:      macros.golang

%description
%{summary}.


# Restore this package if RPM gets fixed (bug #975909)
#%package       data
#Summary:       Required architecture-independent files for Go
#Requires:      %{name} = %{version}-%{release}
#BuildArch:     noarch
#Obsoletes:     %{name}-docs < 1.1-4
#
#%description   data
#%{summary}.


##
# the source tree
%package        src
Summary:        Golang compiler source tree
BuildArch:      noarch
%description    src
%{summary}

##
# This is the only architecture specific binary
%ifarch %{ix86}
%package        pkg-bin-linux-386
Summary:        Golang compiler tool for linux 386
Requires:       go = %{version}-%{release}
Requires:       golang-pkg-linux-386 = %{version}-%{release}
Requires(post): golang-pkg-linux-386 = %{version}-%{release}
Provides:       golang-bin = 386
Provides:       go(API)(go) = %{go_api}
# We strip the meta dependency, but go does require glibc.
# This is an odd issue, still looking for a better fix.
Requires:       glibc
Requires:       gcc
Requires(post): %{_sbindir}/update-alternatives
Requires(postun): %{_sbindir}/update-alternatives
%description    pkg-bin-linux-386
%{summary}
%endif

%ifarch x86_64
%package        pkg-bin-linux-amd64
Summary:        Golang compiler tool for linux amd64
Requires:       go = %{version}-%{release}
Requires:       golang-pkg-linux-amd64 = %{version}-%{release}
Requires(post): golang-pkg-linux-amd64 = %{version}-%{release}
Provides:       golang-bin = amd64
Provides:       go(API)(go) = %{go_api}
# We strip the meta dependency, but go does require glibc.
# This is an odd issue, still looking for a better fix.
Requires:       glibc
Requires:       gcc
Requires(post): %{_sbindir}/update-alternatives
Requires(postun): %{_sbindir}/update-alternatives
%description    pkg-bin-linux-amd64
%{summary}
%endif

%ifarch %{arm}
%package        pkg-bin-linux-arm
Summary:        Golang compiler tool for linux arm
Requires:       go = %{version}-%{release}
Requires:       golang-pkg-linux-arm = %{version}-%{release}
Requires(post): golang-pkg-linux-arm = %{version}-%{release}
Provides:       golang-bin = arm
Provides:       go(API)(go) = %{go_api}
# We strip the meta dependency, but go does require glibc.
# This is an odd issue, still looking for a better fix.
Requires:       glibc
Requires:       gcc
Requires(post): %{_sbindir}/update-alternatives
Requires(postun): %{_sbindir}/update-alternatives
%description    pkg-bin-linux-arm
%{summary}
%endif

##
# architecture independent go tooling, that allows for cross
# compiling on golang supported architectures
# http://golang.org/doc/install/source#environment
%package        pkg-linux-386
Summary:        Golang compiler toolchain to compile for linux 386
Requires:       go = %{version}-%{release}
Provides:       go(API)(cgo) = %{go_api}
BuildArch:      noarch
%description    pkg-linux-386
%{summary}

%package        pkg-linux-amd64
Summary:        Golang compiler toolchain to compile for linux amd64
Requires:       go = %{version}-%{release}
Provides:       go(API)(cgo) = %{go_api}
BuildArch:      noarch
%description    pkg-linux-amd64
%{summary}

%package        pkg-linux-arm
Summary:        Golang compiler toolchain to compile for linux arm
Requires:       go = %{version}-%{release}
Provides:       go(API)(cgo) = %{go_api}
BuildArch:      noarch
%description    pkg-linux-arm
%{summary}

%package        pkg-darwin-386
Summary:        Golang compiler toolchain to compile for darwin 386
Requires:       go = %{version}-%{release}
BuildArch:      noarch
%description    pkg-darwin-386
%{summary}

%package        pkg-darwin-amd64
Summary:        Golang compiler toolchain to compile for darwin amd64
Requires:       go = %{version}-%{release}
BuildArch:      noarch
%description    pkg-darwin-amd64
%{summary}

%package        pkg-windows-386
Summary:        Golang compiler toolchain to compile for windows 386
Requires:       go = %{version}-%{release}
BuildArch:      noarch
%description    pkg-windows-386
%{summary}

%package        pkg-windows-amd64
Summary:        Golang compiler toolchain to compile for windows amd64
Requires:       go = %{version}-%{release}
BuildArch:      noarch
%description    pkg-windows-amd64
%{summary}

#%package        pkg-plan9-386
#Summary:        Golang compiler toolchain to compile for plan9 386
#Requires:       go = %{version}-%{release}
#BuildArch:      noarch
#%description    pkg-plan9-386
#%{summary}

#%package        pkg-plan9-amd64
#Summary:        Golang compiler toolchain to compile for plan9 amd64
#Requires:       go = %{version}-%{release}
#BuildArch:      noarch
#%description    pkg-plan9-amd64
#%{summary}

#%package        pkg-freebsd-386
#Summary:        Golang compiler toolchain to compile for freebsd 386
#Requires:       go = %{version}-%{release}
#BuildArch:      noarch
#%description    pkg-freebsd-386
#%{summary}

#%package        pkg-freebsd-amd64
#Summary:        Golang compiler toolchain to compile for freebsd amd64
#Requires:       go = %{version}-%{release}
#BuildArch:      noarch
#%description    pkg-freebsd-amd64
#%{summary}

#%package        pkg-freebsd-arm
#Summary:        Golang compiler toolchain to compile for freebsd arm
#Requires:       go = %{version}-%{release}
#BuildArch:      noarch
#%description    pkg-freebsd-arm
#%{summary}

#%package        pkg-netbsd-386
#Summary:        Golang compiler toolchain to compile for netbsd 386
#Requires:       go = %{version}-%{release}
#BuildArch:      noarch
#%description    pkg-netbsd-386
#%{summary}

#%package        pkg-netbsd-amd64
#Summary:        Golang compiler toolchain to compile for netbsd amd64
#Requires:       go = %{version}-%{release}
#BuildArch:      noarch
#%description    pkg-netbsd-amd64
#%{summary}

#%package        pkg-netbsd-arm
#Summary:        Golang compiler toolchain to compile for netbsd arm
#Requires:       go = %{version}-%{release}
#BuildArch:      noarch
#%description    pkg-netbsd-arm
#%{summary}

#%package        pkg-openbsd-386
#Summary:        Golang compiler toolchain to compile for openbsd 386
#Requires:       go = %{version}-%{release}
#BuildArch:      noarch
#%description    pkg-openbsd-386
#%{summary}

#%package        pkg-openbsd-amd64
#Summary:        Golang compiler toolchain to compile for openbsd amd64
#Requires:       go = %{version}-%{release}
#BuildArch:      noarch
#%description    pkg-openbsd-amd64
#%{summary}

## missing ./go/src/runtime/defs_openbsd_arm.h
## we'll skip this bundle for now
#%package        pkg-openbsd-arm
#Summary:        Golang compiler toolchain to compile for openbsd arm
#Requires:       go = %{version}-%{release}
#BuildArch:      noarch
#%description    pkg-openbsd-arm
#%{summary}

# Workaround old RPM bug of symlink-replaced-with-dir failure
%pretrans -p <lua>
for _,d in pairs({"api", "doc", "include", "lib", "src"}) do
  path = "%{goroot}/" .. d
  if posix.stat(path, "type") == "link" then
    os.remove(path)
    posix.mkdir(path)
  end
end


%prep
%setup -q -n go

#%if 0%{?fedora} >= 21
#%patch210 -p0
#%patch211 -p1
#%endif

# increase verbosity of build
#%patch0 -p1

# remove the P224 curve
#%patch1 -p1

# disable flanky test
#%patch2 -p1
%build
# set up final install location
export GOROOT_FINAL=%{goroot}

# TODO use the system linker to get the system link flags and build-id
# when https://code.google.com/p/go/issues/detail?id=5221 is solved
#export GO_LDFLAGS="-linkmode external -extldflags $RPM_LD_FLAGS"

export GOHOSTOS=linux
export GOHOSTARCH=%{gohostarch}

# build for all (see http://golang.org/doc/install/source#environment)
pushd src
	for goos in darwin linux windows ; do
		for goarch in 386 amd64 arm ; do
			if [ "${goarch}" = "arm" ] ; then
				if [ "${goos}" = "darwin" -o "${goos}" = "windows" -o "${goos}" = "plan9" -o "${goos}" = "openbsd" ] ;then
					continue
				fi
			fi
			# use our gcc options for this build, but store gcc as default for compiler
			#CC="gcc $RPM_OPT_FLAGS $RPM_LD_FLAGS" \
			CC="gcc" \
			CC_FOR_TARGET="gcc" \
				GOOS=${goos} \
				GOARCH=${goarch} \
				./make.bash --no-clean
		done
	done
popd

%install
rm -rf $RPM_BUILD_ROOT

# create the top level directories
mkdir -p $RPM_BUILD_ROOT%{_bindir}
mkdir -p $RPM_BUILD_ROOT%{goroot}

# install everything into libdir (until symlink problems are fixed)
# https://code.google.com/p/go/issues/detail?id=5830
cp -apv api bin doc favicon.ico lib pkg robots.txt src misc VERSION \
   $RPM_BUILD_ROOT%{goroot}

# bz1099206
find $RPM_BUILD_ROOT%{goroot}/src -exec touch -r $RPM_BUILD_ROOT%{goroot}/VERSION "{}" \;
# and level out all the built archives
touch $RPM_BUILD_ROOT%{goroot}/pkg
find $RPM_BUILD_ROOT%{goroot}/pkg -exec touch -r $RPM_BUILD_ROOT%{goroot}/pkg "{}" \;
# generate the spec file ownership of this source tree and packages
cwd=$(pwd)
src_list=$cwd/go-src.list
rm -f $src_list
touch $src_list
pushd $RPM_BUILD_ROOT%{goroot}
	find src/ -type d -printf '%%%dir %{goroot}/%p\n' >> $src_list
	find src/ ! -type d -printf '%{goroot}/%p\n' >> $src_list


	for goos in darwin linux windows ; do
		for goarch in 386 amd64 arm ; do
			if [ "${goarch}" = "arm" ] ; then
				if [ "${goos}" = "darwin" -o "${goos}" = "windows" ] ;then
					continue
				fi
			fi
			file_list=${cwd}/pkg-${goos}-${goarch}.list
			rm -f $file_list
			touch $file_list
			find pkg/${goos}_${goarch}/ -type d -printf '%%%dir %{goroot}/%p\n' >> $file_list
			find pkg/${goos}_${goarch}/ ! -type d -printf '%{goroot}/%p\n' >> $file_list
		done
	done
popd

# remove the unnecessary zoneinfo file (Go will always use the system one first)
rm -rfv $RPM_BUILD_ROOT%{goroot}/lib/time

# remove the doc Makefile
rm -rfv $RPM_BUILD_ROOT%{goroot}/doc/Makefile

# put binaries to bindir, linked to the arch we're building,
# leave the arch independent pieces in %{goroot}
mkdir -p $RPM_BUILD_ROOT%{goroot}/bin/linux_%{gohostarch}
mv $RPM_BUILD_ROOT%{goroot}/bin/go $RPM_BUILD_ROOT%{goroot}/bin/linux_%{gohostarch}/go
mv $RPM_BUILD_ROOT%{goroot}/bin/gofmt $RPM_BUILD_ROOT%{goroot}/bin/linux_%{gohostarch}/gofmt

# ensure these exist and are owned
mkdir -p $RPM_BUILD_ROOT%{gopath}/src/github.com/
mkdir -p $RPM_BUILD_ROOT%{gopath}/src/bitbucket.org/
mkdir -p $RPM_BUILD_ROOT%{gopath}/src/code.google.com/
mkdir -p $RPM_BUILD_ROOT%{gopath}/src/code.google.com/p/

# remove the go and gofmt for other platforms (not used in the compile)
pushd $RPM_BUILD_ROOT%{goroot}/bin/
	rm -rf darwin_* windows_* freebsd_* netbsd_* openbsd_* plan9_*
	case "%{gohostarch}" in
		amd64)
			rm -rf linux_386 linux_arm ;;
		386)
			rm -rf linux_arm linux_amd64 ;;
		arm)
			rm -rf linux_386 linux_amd64 ;;
	esac
popd

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
export PATH="$PATH":"$GOROOT"/bin
cd src
# skip using CGO for test. causes a SIGABRT on fc21 (bz1086900)
# until this test/issue is fixed
# https://bugzilla.redhat.com/show_bug.cgi?id=1086900
# CGO for test, which fails in i686 on fc21 inside mock/chroot (bz1087621)
# https://bugzilla.redhat.com/show_bug.cgi?id=1087621

# not using our 'gcc' since the CFLAGS fails crash_cgo_test.go due to unused variables
# https://code.google.com/p/go/issues/detail?id=6883
CGO_ENABLED=0 ./run.bash --no-rebuild
cd ..

if [ $(go list -json std | grep Stale | wc -l) -gt 2 ] ; then
	# cmd/go and cmd/gofmt show like they are stale. we can ignore
	exit 1
fi


%ifarch %{ix86}
%post pkg-bin-linux-386
# since the cgo.a packaged in this rpm will be older than the other archives likely built on the ARM builder,
touch -r %{goroot}/pkg/linux_386/runtime.a %{goroot}/pkg/linux_386/runtime/cgo.a

%{_sbindir}/update-alternatives --install %{_bindir}/go \
	go %{goroot}/bin/linux_386/go 90 \
	--slave %{_bindir}/gofmt gofmt %{goroot}/bin/linux_386/gofmt

%preun pkg-bin-linux-386
if [ $1 = 0 ]; then
	%{_sbindir}/update-alternatives --remove go %{goroot}/bin/linux_386/go
fi
%endif

%ifarch x86_64
%post pkg-bin-linux-amd64
# since the cgo.a packaged in this rpm will be older than the other archives likely built on the ARM builder,
touch -r %{goroot}/pkg/linux_amd64/runtime.a %{goroot}/pkg/linux_amd64/runtime/cgo.a

%{_sbindir}/update-alternatives --install %{_bindir}/go \
	go %{goroot}/bin/linux_amd64/go 90 \
	--slave %{_bindir}/gofmt gofmt %{goroot}/bin/linux_amd64/gofmt

%preun pkg-bin-linux-amd64
if [ $1 = 0 ]; then
	%{_sbindir}/update-alternatives --remove go %{goroot}/bin/linux_amd64/go
	touch /usr/bin/go
	touch /usr/bin/gofmt
fi
%endif

%ifarch %{arm}
%post pkg-bin-linux-arm
# since the cgo.a packaged in this rpm will be older than the other archives likely built on the ARM builder,
touch -r %{goroot}/pkg/linux_arm/runtime.a %{goroot}/pkg/linux_arm/runtime/cgo.a

%{_sbindir}/update-alternatives --install %{_bindir}/go \
	go %{goroot}/bin/linux_arm/go 90 \
	--slave %{_bindir}/gofmt gofmt %{goroot}/bin/linux_arm/gofmt

%preun pkg-bin-linux-arm
if [ $1 = 0 ]; then
	%{_sbindir}/update-alternatives --remove go %{goroot}/bin/linux_arm/go
fi
%endif


%files
%doc AUTHORS CONTRIBUTORS LICENSE PATENTS
# VERSION has to be present in the GOROOT, for `go install std` to work
%doc %{goroot}/VERSION
%doc %{goroot}/doc/*

# go files
%dir %{goroot}
%{goroot}/*
%exclude %{goroot}/VERSION
%exclude %{goroot}/bin/
%exclude %{goroot}/pkg/
%exclude %{goroot}/src/

# ensure directory ownership, so they are cleaned up if empty
%dir %{gopath}
%dir %{gopath}/src
%dir %{gopath}/src/github.com/
%dir %{gopath}/src/bitbucket.org/
%dir %{gopath}/src/code.google.com/
%dir %{gopath}/src/code.google.com/p/


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
%exclude %{goroot}/src/debug/elf/testdata/go-relocation-test-gcc482-aarch64.obj
%exclude %{goroot}/src/debug/elf/testdata/gcc-386-freebsd-exec
%exclude %{goroot}/src/debug/elf/testdata/gcc-amd64-openbsd-debug-with-rela.obj

%ifarch %{ix86}
%files pkg-bin-linux-386
%{goroot}/bin/linux_386/
# binary executables
%{_bindir}/go
%{_bindir}/gofmt
%dir %{goroot}/pkg/obj/linux_386
#%{goroot}/pkg/obj/linux_386/*
%{goroot}/pkg/linux_386/runtime/cgo.a
%dir %{goroot}/pkg/tool/linux_386
%{goroot}/pkg/tool/linux_386/addr2line
%{goroot}/pkg/tool/linux_386/api
%{goroot}/pkg/tool/linux_386/asm
%{goroot}/pkg/tool/linux_386/compile
%{goroot}/pkg/tool/linux_386/cover
%{goroot}/pkg/tool/linux_386/dist
%{goroot}/pkg/tool/linux_386/doc
%{goroot}/pkg/tool/linux_386/link
%{goroot}/pkg/tool/linux_386/nm
%{goroot}/pkg/tool/linux_386/objdump
%{goroot}/pkg/tool/linux_386/pack
%{goroot}/pkg/tool/linux_386/pprof
%{goroot}/pkg/tool/linux_386/trace
%{goroot}/pkg/tool/linux_386/vet
%endif

%ifarch x86_64
%files pkg-bin-linux-amd64
%{goroot}/bin/linux_amd64/
# binary executables
%{_bindir}/go
%{_bindir}/gofmt
%dir %{goroot}/pkg/obj/linux_amd64
#%{goroot}/pkg/obj/linux_amd64/*
%{goroot}/pkg/linux_amd64/runtime/cgo.a
%dir %{goroot}/pkg/tool/linux_amd64
%{goroot}/pkg/tool/linux_amd64/addr2line
%{goroot}/pkg/tool/linux_amd64/api
%{goroot}/pkg/tool/linux_amd64/asm
%{goroot}/pkg/tool/linux_amd64/compile
%{goroot}/pkg/tool/linux_amd64/cover
%{goroot}/pkg/tool/linux_amd64/dist
%{goroot}/pkg/tool/linux_amd64/doc
%{goroot}/pkg/tool/linux_amd64/link
%{goroot}/pkg/tool/linux_amd64/nm
%{goroot}/pkg/tool/linux_amd64/objdump
%{goroot}/pkg/tool/linux_amd64/pack
%{goroot}/pkg/tool/linux_amd64/pprof
%{goroot}/pkg/tool/linux_amd64/trace
%{goroot}/pkg/tool/linux_amd64/vet
%endif

%ifarch %{arm}
%files pkg-bin-linux-arm
%{goroot}/bin/linux_arm/
# binary executables
%{_bindir}/go
%{_bindir}/gofmt
%dir %{goroot}/pkg/obj/linux_arm
#%{goroot}/pkg/obj/linux_arm/*
%{goroot}/pkg/linux_arm/runtime/cgo.a
%dir %{goroot}/pkg/tool/linux_arm
%{goroot}/pkg/tool/linux_arm/addr2line
%{goroot}/pkg/tool/linux_arm/api
%{goroot}/pkg/tool/linux_arm/asm
%{goroot}/pkg/tool/linux_arm/compile
%{goroot}/pkg/tool/linux_arm/cover
%{goroot}/pkg/tool/linux_arm/dist
%{goroot}/pkg/tool/linux_arm/doc
%{goroot}/pkg/tool/linux_arm/link
%{goroot}/pkg/tool/linux_arm/nm
%{goroot}/pkg/tool/linux_arm/objdump
%{goroot}/pkg/tool/linux_arm/pack
%{goroot}/pkg/tool/linux_arm/pprof
%{goroot}/pkg/tool/linux_arm/trace
%{goroot}/pkg/tool/linux_arm/vet
%endif

%files pkg-linux-386 -f pkg-linux-386.list
%{goroot}/pkg/linux_386/
%ifarch %{ix86}
%exclude %{goroot}/pkg/linux_386/runtime/cgo.a
%endif
%{goroot}/pkg/tool/linux_386/cgo
%{goroot}/pkg/tool/linux_386/fix
%{goroot}/pkg/tool/linux_386/yacc

%files pkg-linux-amd64 -f pkg-linux-amd64.list
%{goroot}/pkg/linux_amd64/
%ifarch x86_64
%exclude %{goroot}/pkg/linux_amd64/runtime/cgo.a
%endif
%{goroot}/pkg/tool/linux_amd64/cgo
%{goroot}/pkg/tool/linux_amd64/fix
%{goroot}/pkg/tool/linux_amd64/yacc

%files pkg-linux-arm -f pkg-linux-arm.list
%{goroot}/pkg/linux_arm/
%ifarch %{arm}
%exclude %{goroot}/pkg/linux_arm/runtime/cgo.a
%endif
%{goroot}/pkg/tool/linux_arm/cgo
%{goroot}/pkg/tool/linux_arm/fix
%{goroot}/pkg/tool/linux_arm/yacc

%files pkg-darwin-386 -f pkg-darwin-386.list
%{goroot}/pkg/darwin_386/
%{goroot}/pkg/tool/darwin_386/

%files pkg-darwin-amd64 -f pkg-darwin-amd64.list
%{goroot}/pkg/darwin_amd64/
%{goroot}/pkg/tool/darwin_amd64/

%files pkg-windows-386 -f pkg-windows-386.list
%{goroot}/pkg/windows_386/
%{goroot}/pkg/tool/windows_386/

%files pkg-windows-amd64 -f pkg-windows-amd64.list
%{goroot}/pkg/windows_amd64/
%{goroot}/pkg/tool/windows_amd64/

#%files pkg-plan9-386 -f pkg-plan9-386.list
#%{goroot}/pkg/plan9_386/
#%{goroot}/pkg/tool/plan9_386/

#%files pkg-plan9-amd64 -f pkg-plan9-amd64.list
#%{goroot}/pkg/plan9_amd64/
#%{goroot}/pkg/tool/plan9_amd64/

#%files pkg-freebsd-386 -f pkg-freebsd-386.list
#%{goroot}/pkg/freebsd_386/
#%{goroot}/pkg/tool/freebsd_386/

#%files pkg-freebsd-amd64 -f pkg-freebsd-amd64.list
#%{goroot}/pkg/freebsd_amd64/
#%{goroot}/pkg/tool/freebsd_amd64/

#%files pkg-freebsd-arm -f pkg-freebsd-arm.list
#%{goroot}/pkg/freebsd_arm/
#%{goroot}/pkg/tool/freebsd_arm/

#%files pkg-netbsd-386 -f pkg-netbsd-386.list
#%{goroot}/pkg/netbsd_386/
#%{goroot}/pkg/tool/netbsd_386/

#%files pkg-netbsd-amd64 -f pkg-netbsd-amd64.list
#%{goroot}/pkg/netbsd_amd64/
#%{goroot}/pkg/tool/netbsd_amd64/

#%files pkg-netbsd-arm -f pkg-netbsd-arm.list
#%{goroot}/pkg/netbsd_arm/
#%{goroot}/pkg/tool/netbsd_arm/

#%files pkg-openbsd-386 -f pkg-openbsd-386.list
#%{goroot}/pkg/openbsd_386/
#%{goroot}/pkg/tool/openbsd_386/

#%files pkg-openbsd-amd64 -f pkg-openbsd-amd64.list
#%{goroot}/pkg/openbsd_amd64/
#%{goroot}/pkg/tool/openbsd_amd64/

## skipping for now
#%files pkg-openbsd-arm
#%{goroot}/pkg/openbsd_arm/
#%{goroot}/pkg/tool/openbsd_arm/


%changelog
* Tue Jun 30 2015 Tomas Hrcka <thrcka@redhat.com> - 1.4.2-9
- Enable tests during build time
- Disable building of *BSD sub packages

* Fri Jun 12 2015 Tomas Hrcka <thrcka@redhat.com> - 1.4.2-6
- Resolves: rhbz#1206063

* Fri May 08 2015 Lokesh Mandvekar <lsm5@redhat.com> - 1.4.2-4
- Revert previous build
- bring back non-linux and non-x86_64 subpackages

* Mon May 04 2015 Lokesh Mandvekar <lsm5@redhat.com> - 1.4.2-3
- update to 1.4.2 (iterative build)
- remove non-linux and non-x86_64 subpackages

* Mon May 04 2015 Lokesh Mandvekar <lsm5@redhat.com> - 1.4.2-2
- update to 1.4.2 (iterative build)
- emacs and vim subpackages obsoleted as they're no longer provided

* Fri Apr 17 2015 Lokesh Mandvekar <lsm5@redhat.com> - 1.4.2-1
- update to 1.4.2 - initial build
- recompile CentOS7 virt SIG srpm for rhel7

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

* Thu Sep 11 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3.1-3
- patching the tzinfo failure

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Wed Aug 13 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3.1-1
- update to go1.3.1

* Wed Aug 13 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3-11
- merged a line wrong

* Wed Aug 13 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3-10
- more work to get cgo.a timestamps to line up, due to build-env
- explicitly list all the files and directories for the source and packages trees
- touch all the built archives to be the same

* Mon Aug 11 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3-9
- make golang-src 'noarch' again, since that was not a fix, and takes up more space

* Mon Aug 11 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3-8
- update timestamps of source files during %%install bz1099206

* Fri Aug 08 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3-7
- update timestamps of source during %%install bz1099206

* Wed Aug 06 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3-6
- make the source subpackage arch'ed, instead of noarch

* Mon Jul 21 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3-5
- fix the writing of pax headers

* Tue Jul 15 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3-4
- fix the loading of gdb safe-path. bz981356

* Tue Jul 08 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3-3
- `go install std` requires gcc, to build cgo. bz1105901, bz1101508

* Mon Jul 07 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3-2
- archive/tar memory allocation improvements

* Thu Jun 19 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3-1
- update to go1.3

* Fri Jun 13 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.3rc2-1
- update to go1.3rc2

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3rc1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue Jun 03 2014 Vincent Batts <vbatts@redhat.com> 1.3rc1-1
- update to go1.3rc1
- new arch file shuffling

* Wed May 21 2014 Vincent Batts <vbatts@redhat.com> 1.3beta2-1
- update to go1.3beta2
- no longer provides go-mode for xemacs (emacs only)

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

* Fri Aug 30 2013 Adam Miller <maxamillion@fedoraproject.org> - 1.1.2-4
- fix the libc meta dependency (thanks to vbatts [at] redhat.com for the fix)

* Tue Aug 27 2013 Adam Miller <maxamillion@fedoraproject.org> - 1.1.2-3
- Revert incorrect merged changelog

* Tue Aug 27 2013 Adam Miller <maxamillion@fedoraproject.org> - 1.1.2-2
- This was reverted, just a placeholder changelog entry for bad merge

* Tue Aug 20 2013 Adam Miller <maxamillion@fedoraproject.org> - 1.1.2-1
- Update to latest upstream

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.1-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Jul 17 2013 Petr Pisar <ppisar@redhat.com> - 1.1.1-6
- Perl 5.18 rebuild

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
