%global fb303_version 1.0.0.dev0

%global py_version 2.7

%global php_extdir  %(php-config --extension-dir 2>/dev/null || echo "undefined")

%{?perl_default_filter}
%global __provides_exclude_from ^(%{python_sitearch}/.*\\.so|%{php_extdir}/.*\\.so)$

%global have_mongrel 0

# erlang-jsx is available in F19 but orphaned in F22
%global have_jsx 0

# We should be able to enable this in the future
%global want_d 0

# Thrift's Ruby support depends on Mongrel.  Since Mongrel is
# deprecated in Fedora, we can't support Ruby bindings for Thrift
# unless and until Thrift is patched to use a different HTTP server.
%if 0%{?have_mongrel} == 0
%global ruby_configure --without-ruby
%global with_ruby 0
%else
%global ruby_configure --with-ruby
%global want_ruby 1
%endif

# Thrift's Erlang support depends on the JSX library, which is not
# currently available in Fedora.

%if 0%{?have_jsx} == 0
%global erlang_configure --without-erlang
%global want_erlang 0
%else
%global erlang_configure --with-erlang
%global want_erlang 1
%endif

# PHP appears broken in Thrift 0.9.1
%global want_php 0

%if 0%{?want_php} == 0
%global php_langname %{nil}
%global php_configure --without-php
%else
%global php_langname PHP,\ 
%global php_configure --with-php
%endif

# Thrift's GO support doesn't build under Fedora
%global want_golang 0
%global golang_configure --without-go

Name:    thrift
Version: 0.10.0
Release: 1%{?dist}
Summary: Software framework for cross-language services development

# Parts of the source are used under the BSD and zlib licenses, but
# these are OK for inclusion in an Apache 2.0-licensed whole:
# https://www.apache.org/legal/3party.html

# Here's the breakdown:
# ./lib/py/compat/win32/stdint.h is 2-clause BSD
# ./compiler/cpp/src/md5.[ch] are zlib
License: ASL 2.0 and BSD and zlib
URL:     https://thrift.apache.org/

Source0: https://archive.apache.org/dist/%{name}/%{version}/%{name}-%{version}.tar.gz

Source1: https://repo1.maven.org/maven2/org/apache/thrift/lib%{name}/%{version}/lib%{name}-%{version}.pom
Source2: https://raw.github.com/apache/%{name}/%{version}/bootstrap.sh

Source3: https://gitorious.org/pkg-scribe/thrift-deb-pkg/raw/master:debian/manpage.1.ex
Source4: https://repo1.maven.org/maven2/org/apache/thrift/libfb303/%{version}/libfb303-%{version}.pom

# this patch is adapted from Gil Cattaneo's thrift-0.7.0 package
Patch0: %{name}-%{version}-buildxml.patch
# for fb303, excise maven ant tasks; build against system libraries; etc.
Patch1: fb303-%{version}-buildxml.patch
# fix configure.ac insistence on using /usr/local/lib for JAVA_PREFIX
Patch2: configure-java-prefix.patch

Group: Development/Libraries

# BuildRequires for language-specific bindings are listed under these
# subpackages, to facilitate enabling or disabling individual language
# bindings in the future

BuildRequires: ant >= 1.7
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: bison
BuildRequires: boost-devel
BuildRequires: flex
BuildRequires: flex-devel
BuildRequires: glib2-devel
BuildRequires: libstdc++-devel
BuildRequires: libtool
BuildRequires: openssl-devel
BuildRequires: qt-devel
BuildRequires: texlive
BuildRequires: zlib-devel

%if 0%{?want_golang} > 0
BuildRequires: golang
Requires: golang
%endif

%description

The Apache Thrift software framework for cross-language services
development combines a software stack with a code generation engine to
build services that work efficiently and seamlessly between C++, Java,
Python, %{?php_langname}and other languages.

%package devel
Summary: Development files for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: pkgconfig
Requires: boost-devel

%description devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%package        qt
Summary:        Qt support for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    qt
The %{name}-qt package contains Qt bindings for %{name}.

%package        glib
Summary:        GLib support for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    glib
The %{name}-qt package contains GLib bindings for %{name}.

%package -n python-%{name}
Summary: Python support for %{name}
BuildRequires: python2-devel
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: python2

%description -n python-%{name}
The python-%{name} package contains Python bindings for %{name}.

%package -n perl-%{name}
Summary: Perl support for %{name}
Provides: perl(Thrift) = %{version}-%{release}
BuildRequires: perl(Bit::Vector)
BuildRequires: perl(Class::Accessor)
BuildRequires: perl(ExtUtils::MakeMaker)
BuildRequires: perl-generators
Requires: perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
Requires: perl(Bit::Vector)
Requires: perl(Encode)
Requires: perl(HTTP::Request)
Requires: perl(IO::Select)
Requires: perl(IO::Socket::INET)
Requires: perl(IO::String)
Requires: perl(LWP::UserAgent)
Requires: perl(POSIX)
Requires: perl(base)
Requires: perl(constant)
Requires: perl(strict)
Requires: perl(utf8)
Requires: perl(warnings)
BuildArch: noarch

%description -n perl-%{name}
The perl-%{name} package contains Perl bindings for %{name}.

%if %{?want_d}
%package -n d-%{name}
Summary: D support for %{name}
BuildRequires: ldc

%description -n d-%{name}
The d-%{name} package contains D bindings for %{name}.
%endif

%if 0%{?want_php} != 0
%package -n php-%{name}
Summary: PHP support for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: php(zend-abi) = %{php_zend_api}
Requires: php(api) = %{php_core_api}
Requires: php(language) >= 5.3.0
Requires: php-date
Requires: php-json
BuildRequires: php-devel

%description -n php-%{name}
The php-%{name} package contains PHP bindings for %{name}.
%endif

%package -n lib%{name}-javadoc
Summary: API documentation for java-%{name}
Requires: lib%{name}-java = %{version}-%{release}
BuildArch: noarch

%description -n lib%{name}-javadoc 
The lib%{name}-javadoc package contains API documentation for the
Java bindings for %{name}.

%package -n lib%{name}-java
Summary: Java support for %{name}

BuildRequires: apache-commons-codec
BuildRequires: apache-commons-lang
BuildRequires: apache-commons-logging
BuildRequires: httpcomponents-client
BuildRequires: httpcomponents-core
BuildRequires: java-devel
BuildRequires: javapackages-tools
BuildRequires: junit
BuildRequires: log4j
BuildRequires: slf4j
BuildRequires: tomcat-servlet-3.1-api

Requires: java-headless >= 1:1.6.0
Requires: javapackages-tools
Requires: mvn(org.slf4j:slf4j-api)
Requires: mvn(commons-lang:commons-lang)
Requires: mvn(org.apache.httpcomponents:httpclient)
Requires: mvn(org.apache.httpcomponents:httpcore)
BuildArch: noarch


%description -n lib%{name}-java
The lib%{name}-java package contains Java bindings for %{name}.

%if 0%{?want_ruby} > 0
%package -n ruby-%{name}
Summary: Ruby support for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: ruby(release)
BuildRequires: ruby-devel

%description -n ruby-%{name}
The ruby-%{name} package contains Ruby bindings for %{name}.
%endif

%if 0%{?want_erlang} > 0
%package -n erlang-%{name}
Summary: Erlang support for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: erlang
Requires: erlang-jsx
BuildRequires: erlang
BuildRequires: erlang-rebar

%description -n erlang-%{name}
The erlang-%{name} package contains Erlang bindings for %{name}.
%endif

%package -n fb303
Summary: Basic interface for Thrift services
Requires: %{name}%{?_isa} = %{version}-%{release}

%description -n fb303
fb303 is the shared root of all Thrift services; it provides a
standard interface to monitoring, dynamic options and configuration,
uptime reports, activity, etc.

%package -n fb303-devel
Summary: Development files for fb303
Requires: fb303%{?_isa} = %{version}-%{release}

%description -n fb303-devel
The fb303-devel package contains header files for fb303

%package -n python-fb303
Summary: Python bindings for fb303
Requires: fb303%{?_isa} = %{version}-%{release}
BuildRequires: python2-devel

%description -n python-fb303
The python-fb303 package contains Python bindings for fb303.

%package -n fb303-java
Summary: Java bindings for fb303
Requires: java >= 1:1.6.0
Requires: javapackages-tools
Requires: mvn(org.slf4j:slf4j-api)
Requires: mvn(commons-lang:commons-lang)
Requires: mvn(org.apache.httpcomponents:httpclient)
Requires: mvn(org.apache.httpcomponents:httpcore)
BuildArch: noarch

%description -n fb303-java
The fb303-java package contains Java bindings for fb303.

%global _default_patch_fuzz 2
%prep
%autosetup -p1

%{?!el5:sed -i -e 's/^AC_PROG_LIBTOOL/LT_INIT/g' configure.ac}

# avoid spurious executable permissions in debuginfo package
find . -name \*.cpp -or -name \*.cc -or -name \*.h | xargs -r chmod 644

cp -p %{SOURCE2} bootstrap.sh

# work around linking issues
echo 'libthrift_c_glib_la_LIBADD = $(GLIB_LIBS) $(GOBJECT_LIBS) -L../cpp/.libs ' >> lib/c_glib/Makefile.am
echo 'libthriftqt_la_LIBADD = $(QT_LIBS) -lthrift -L.libs' >> lib/cpp/Makefile.am
echo 'libthriftz_la_LIBADD = $(ZLIB_LIBS) -lthrift -L.libs' >> lib/cpp/Makefile.am
echo 'EXTRA_libthriftqt_la_DEPENDENCIES = libthrift.la' >> lib/cpp/Makefile.am
echo 'EXTRA_libthriftz_la_DEPENDENCIES = libthrift.la' >> lib/cpp/Makefile.am

# echo 'libfb303_so_LIBADD = -lthrift -L../../../lib/cpp/.libs' >> contrib/fb303/cpp/Makefile.am

sed -i 's|libfb303_so_LDFLAGS = $(SHARED_LDFLAGS)|libfb303_so_LDFLAGS = $(SHARED_LDFLAGS) -lthrift -L../../../lib/cpp/.libs -Wl,--as-needed|g' contrib/fb303/cpp/Makefile.am

# fix broken upstream check for ant version; we enforce this with BuildRequires, so no need to check here
sed -i 's|ANT_VALID=.*|ANT_VALID=1|' aclocal/ax_javac_and_java.m4
sed -i 's|ANT_VALID=.*|ANT_VALID=1|' contrib/fb303/aclocal/ax_javac_and_java.m4

%build
export PY_PREFIX=%{_prefix}
export PERL_PREFIX=%{_prefix}
export PHP_PREFIX=%{php_extdir}
export JAVA_PREFIX=%{_javadir}
export RUBY_PREFIX=%{_prefix}
export GLIB_LIBS=$(pkg-config --libs glib-2.0)
export GLIB_CFLAGS=$(pkg-config --cflags glib-2.0)
export GOBJECT_LIBS=$(pkg-config --libs gobject-2.0)
export GOBJECT_CFLAGS=$(pkg-config --cflags gobject-2.0)

find %{_builddir} -name rebar -exec rm -f '{}' \;
find . -name Makefile\* -exec sed -i -e 's/[.][/]rebar/rebar/g' {} \;

# install javadocs in proper places
sed -i 's|-Dinstall.javadoc.path=$(DESTDIR)$(docdir)/java|-Dinstall.javadoc.path=$(DESTDIR)%{_javadocdir}/%{name}|' lib/java/Makefile.*

# build a jar without a version number
sed -i 's|${thrift.artifactid}-${version}|${thrift.artifactid}|' lib/java/build.xml

# Proper permissions for Erlang files
sed -i 's|$(INSTALL) $$p|$(INSTALL) --mode 644 $$p|g' lib/erl/Makefile.am

# Build fb303 jars against the in-situ copy of thrift
sed -i 's|$(thrift_home)/bin/thrift|../../../compiler/cpp/thrift|g' \
 contrib/fb303/cpp/Makefile.am \
 contrib/fb303/py/Makefile.am

sed -i 's|$(prefix)/lib$|%{_libdir}|g' contrib/fb303/cpp/Makefile.am

sed -i 's|$(thrift_home)/include/thrift|../../../lib/cpp/src|g' \
 contrib/fb303/cpp/Makefile.am

# Create a straightforward makefile for Java fb303
echo "all:
	ant
install: build/libfb303.jar
	mkdir -p %{buildroot}%{_javadir}
	/usr/bin/install -c -m 644 build/libfb303.jar %{buildroot}%{_javadir}
" > contrib/fb303/java/Makefile

sh ./bootstrap.sh

# use unversioned doc dirs where appropriate (via _pkgdocdir macro)
%configure --disable-dependency-tracking --disable-static --without-libevent --with-boost=/usr %{ruby_configure} %{erlang_configure} %{golang_configure} %{php_configure} --docdir=%{?_pkgdocdir}%{!?_pkgdocdir:%{_docdir}/%{name}-%{version}}

# eliminate unused direct shlib dependencies
sed -i -e 's/ -shared / -Wl,--as-needed\0/g' libtool

make %{?_smp_mflags}

# build fb303
(
  cd contrib/fb303
  sed -i '/^[.][/]configure.*/d' bootstrap.sh
  sh bootstrap.sh
  %configure --disable-static --with-java --without-php --libdir=%{_libdir}
  make %{?_smp_mflags}
  (
      cd java
      ant dist
  )
)

%install
%make_install
find %{buildroot} -name '*.la' -exec rm -f {} ';'
find %{buildroot} -name fastbinary.so | xargs -r chmod 755
find %{buildroot} -name \*.erl -or -name \*.hrl -or -name \*.app | xargs -r chmod 644

# install man page
mkdir -p %{buildroot}%{_mandir}/man1
cp %{SOURCE3} %{buildroot}%{_mandir}/man1/thrift.1
gzip -9v %{buildroot}%{_mandir}/man1/thrift.1

# Remove javadocs jar
find %{buildroot}/%{_javadir} -name lib%{name}-javadoc.jar -exec rm -f '{}' \;

# Add POM file and depmap
mkdir -p %{buildroot}%{_mavenpomdir}

install -pm 644 %{SOURCE1} %{buildroot}%{_mavenpomdir}/JPP-libthrift.pom

%add_maven_depmap JPP-libthrift.pom libthrift.jar

# Remove bundled jar files
find %{buildroot} -name \*.jar -a \! -name \*thrift\* -exec rm -f '{}' \;

# Move perl files into appropriate places
find %{buildroot} -name \*.pod -exec rm -f '{}' \;
find %{buildroot} -name .packlist -exec rm -f '{}' \;
find %{buildroot}/usr/lib/perl5 -type d -empty -delete
mkdir -p %{buildroot}/%{perl_vendorlib}/
mv %{buildroot}/usr/lib/perl5/* %{buildroot}/%{perl_vendorlib}

%if 0%{?want_php} != 0

# Move arch-independent php files into the appropriate place
mkdir -p %{buildroot}/%{_datadir}/php/
mv %{buildroot}/%{php_extdir}/Thrift %{buildroot}/%{_datadir}/php/
%endif # want_php

# Fix permissions on Thread.h
find %{buildroot} -name Thread.h -exec chmod a-x '{}' \;

# install fb303
(
  cd contrib/fb303
  make DESTDIR=%{buildroot} install
  (
    cd java
    ant -Dinstall.path=%{buildroot}%{_javadir} -Dinstall.javadoc.path=%{buildroot}%{_javadocdir}/fb303 install
  )
)

# install maven pom and depmaps for fb303
install -pm 644 %{SOURCE4} %{buildroot}%{_mavenpomdir}/JPP-libfb303.pom
%add_maven_depmap JPP-libfb303.pom libfb303.jar -f "fb303"

# Ensure all python scripts are executable
find %{buildroot} -name \*.py -exec grep -q /usr/bin/env {} \; -print | xargs -r chmod 755


%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%files
%doc LICENSE NOTICE
%{_bindir}/thrift
%{_libdir}/libthrift-%{version}.so
%{_libdir}/libthriftz-%{version}.so
%{_mandir}/man1/thrift.1.gz

%files glib
%{_libdir}/libthrift_c_glib.so
%{_libdir}/libthrift_c_glib.so.*

%files qt
%{_libdir}/libthriftqt.so
%{_libdir}/libthriftqt-%{version}.so

%files devel
%{_includedir}/thrift
%exclude %{_includedir}/thrift/fb303
%{_libdir}/*.so
%{_libdir}/*.so.0
%{_libdir}/*.so.0.0.0
%exclude %{_libdir}/lib*-%{version}.so
%exclude %{_libdir}/libfb303.so
%{_libdir}/pkgconfig/thrift-z.pc
%{_libdir}/pkgconfig/thrift-qt.pc
%{_libdir}/pkgconfig/thrift.pc
%{_libdir}/pkgconfig/thrift_c_glib.pc
%doc LICENSE NOTICE

%files -n perl-%{name}
%{perl_vendorlib}/Thrift
%{perl_vendorlib}/Thrift.pm
%doc LICENSE NOTICE

%if 0%{?want_php} != 0
%files -n php-%{name}
%config(noreplace) /etc/php.d/thrift_protocol.ini
%{_datadir}/php/Thrift/
%{php_extdir}/thrift_protocol.so
%doc LICENSE NOTICE
%endif

%if %{?want_erlang} > 0
%files -n erlang-%{name}
%{_libdir}/erlang/lib/%{name}-%{version}/
%doc LICENSE NOTICE
%endif

%files -n python-%{name}
%{python_sitearch}/%{name}
%{python_sitearch}/%{name}-%{version}-py%{py_version}.egg-info
%doc LICENSE NOTICE

%files -n lib%{name}-javadoc
%{_javadocdir}/%{name}
%doc LICENSE NOTICE

%files -n lib%{name}-java -f .mfiles
%doc LICENSE NOTICE

%files -n fb303
%{_datarootdir}/fb303
%doc LICENSE NOTICE

%files -n fb303-devel
%{_libdir}/libfb303.so
%{_includedir}/thrift/fb303
%doc LICENSE NOTICE

%files -n python-fb303
%{python_sitelib}/fb303
%{python_sitelib}/fb303_scripts
%{python_sitelib}/%{name}_fb303-%{version}-py%{py_version}.egg-info
%doc LICENSE NOTICE

%files -n fb303-java -f .mfiles-fb303
%doc LICENSE NOTICE

%changelog
* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.1-17.6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.1-17.5
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Tue May 17 2016 Jitka Plesnikova <jplesnik@redhat.com> - 0.9.1-17.4
- Perl 5.24 rebuild

* Wed Mar 30 2016 Petr Pisar <ppisar@redhat.com> - 0.9.1-17.3
- Adapt to GCC 6 (bug #1306671)

* Fri Feb 05 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.1-17.2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Sat Jan 16 2016 Jonathan Wakely <jwakely@redhat.com> - 0.9.1-17.1
- Rebuilt for Boost 1.60

* Mon Nov 23 2015 Peter Robinson <pbrobinson@fedoraproject.org> 0.9.1-17
- Fix release

* Wed Oct 21 2015 Marcin Juszkiewicz <mjuszkiewicz@redhat.com> - 0.9.1-16.6
- Backport THRIFT-2214 fix to get package built on aarch64.

* Thu Aug 27 2015 Jonathan Wakely <jwakely@redhat.com> - 0.9.1-16.5
- Rebuilt for Boost 1.59

* Wed Jul 29 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.1-16.4
- Rebuilt for https://fedoraproject.org/wiki/Changes/F23Boost159

* Wed Jul 22 2015 David Tardon <dtardon@redhat.com> - 0.9.1-16.3
- rebuild for Boost 1.58

* Fri Jun 19 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.1-16.2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sat Jun 06 2015 Jitka Plesnikova <jplesnik@redhat.com> - 0.9.1-16.1
- Perl 5.22 rebuild

* Fri Apr 24 2015 Michal Srb <msrb@redhat.com> - 0.9.1-16
- Fix FTBFS (Resolves: rhbz#1195364)

* Mon Apr 20 2015 Will Benton <willb@redhat.com> - 0.9.1-15
- Dropped Erlang support for F22 and above, since erlang-jsx is orphaned

* Wed Apr  8 2015 Haïkel Guémar <hguemar@fedoraproject.org> - 0.9.1-14
- Split Qt4/GLib runtimes into separate subpackages
- Drop mono support, it's broken and not even shipped (and it pulls mono-core)

* Mon Jan 26 2015 Petr Machata <pmachata@redhat.com> - 0.9.1-13.3
- Rebuild for boost 1.57.0

* Thu Aug 28 2014 Jitka Plesnikova <jplesnik@redhat.com> - 0.9.1-13.2
- Perl 5.20 rebuild

* Mon Aug 18 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.1-13.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Fri Jun 27 2014 Petr Pisar <ppisar@redhat.com> - 0.9.1-13
- Use add_maven_depmap-generated file lists (bug #1107448)

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.1-12.2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri May 23 2014 Petr Machata <pmachata@redhat.com> - 0.9.1-12.1
- Rebuild for boost 1.55.0

* Mon May 05 2014 Lubomir Rintel <lkundrak@v3.sk> - 0.9.1-12
- Fix EPEL build

* Fri Feb 21 2014 willb <willb@redhat> - 0.9.1-11
- fix BZ 1068561

* Fri Dec 20 2013 willb <willb@redhat> - 0.9.1-10
- fix BZ 1045544

* Wed Oct 16 2013 willb <willb@redhat> - 0.9.1-9
- Remove spurious dependencies
- Move some versioned shared libraries from -devel

* Wed Oct 16 2013 Dan Horák <dan[at]danny.cz> - 0.9.1-8
- Mono available only on selected arches

* Sun Oct 13 2013 willb <willb@redhat> - 0.9.1-7
- minor specfile cleanups

* Fri Oct 11 2013 willb <willb@redhat> - 0.9.1-6
- added thrift man page
- integrated fb303
- fixed many fb303 library dependency problems

* Tue Oct 1 2013 willb <willb@redhat> - 0.9.1-5
- fixed extension library linking when an older thrift package is not
  already installed
- fixed extension library dependencies in Makefile

* Tue Oct 1 2013 willb <willb@redhat> - 0.9.1-4
- addresses rpmlint warnings and errors
- properly links glib, qt, and z extension libraries

* Mon Sep 30 2013 willb <willb@redhat> - 0.9.1-3
- adds QT support
- clarified multiple licensing
- uses parallel make
- removes obsolete M4 macros
- specifies canonical location for source archive

* Tue Sep 24 2013 willb <willb@redhat> - 0.9.1-2
- fixes for i686
- fixes bogus requires for Java package

* Fri Sep 20 2013 willb <willb@redhat> - 0.9.1-1
- updated to upstream version 0.9.1
- disables PHP support, which FTBFS in this version

* Fri Sep 20 2013 willb <willb@redhat> - 0.9.0-5
- patch build xml to generate unversioned jars instead of moving after the fact
- unversioned doc dirs on Fedora versions where this is appropriate
- replaced some stray hardcoded paths with macros
- thanks to Gil for the above observations and suggestions for fixes

* Thu Aug 22 2013 willb <willb@redhat> - 0.9.0-4
- removed version number from jar name (obs pmackinn)

* Thu Aug 22 2013 willb <willb@redhat> - 0.9.0-3
- Fixes for F19 and Erlang support

* Thu Aug 15 2013 willb <willb@redhat> - 0.9.0-2
- Incorporates feedback from comments on review request

* Mon Jul 1 2013 willb <willb@redhat> - 0.9.0-1
- Initial package
