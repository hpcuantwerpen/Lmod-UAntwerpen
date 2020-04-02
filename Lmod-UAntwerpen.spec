%global macrosdir %(d=%{_rpmconfigdir}/macros.d; [ -d $d ] || d=%{_sysconfdir}/rpm; echo $d)

Name:           Lmod
Version:        8.3.6
Release:        1.ua%{?dist}
Summary:        Environmental Modules System in Lua

# Lmod-5.3.2/tools/base64.lua is LGPLv2
License:        MIT and LGPLv2
URL:            https://www.tacc.utexas.edu/tacc-projects/lmod
Source0:        https://github.com/TACC/Lmod/archive/%{version}.tar.gz#/Lmod-%{version}.tar.gz
Source1:        macros.%{name}
Source2:        SitePackage.lua
Source3:        run_lmod_cache.py
Source4:        admin.list
Patch0:         Lmod-spider-no-hidden-cluster-modules.patch

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
# Lmod 8.x ships binaries when configured with --with-fastTCLInterp=yes (which is the default)
# BuildArch:      noarch
BuildRequires:  lua-devel
BuildRequires:  lua-filesystem
BuildRequires:  lua-json
BuildRequires:  lua-posix
BuildRequires:  lua-term
BuildRequires:  tcl-devel
Requires:       lua-filesystem
Requires:       lua-json
Requires:       lua-posix
Requires:       lua-term
Requires:       tcl
Requires:       /bin/ps
# Cannot put conflict on environment-modules because of
# conflict with modules-oscar (nec) otherwise
#Conflicts:      environment-modules

%description
Lmod is a Lua based module system that easily handles the MODULEPATH
Hierarchical problem.  Environment Modules provide a convenient way to
dynamically change the users' environment through modulefiles. This includes
easily adding or removing directories to the PATH environment variable.
Modulefiles for library packages provide environment variables that specify
where the library and header files can be found.


%prep
%setup -q
%patch0 -p1
sed -i -e 's,/usr/bin/env ,/usr/bin/,' src/*.tcl
# Remove bundled lua-term
rm -r pkgs/luafilesystem/ pkgs/term/ tools/json.lua
sed -i -e 's/^spiderCacheSupport: lfs/spiderCacheSupport: /' Makefile.in
# Remove unneeded shbangs
sed -i -e '/^#!/d' init/*.in


%build
%configure --prefix=%{_datadir} PS=/bin/ps --with-caseIndependentSorting=yes --with-redirect=yes --with-shortTime=86400 --with-pinVersions=yes --with-siteName='CalcUA'
make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT

%make_install
# init scripts are sourced
find %{buildroot}%{_datadir}/lmod/%{version}/init/ -type f -print0 | xargs -0 chmod -x
mkdir -p %{buildroot}%{_sysconfdir}/modulefiles
mkdir -p %{buildroot}%{_datadir}/modulefiles
mkdir -p %{buildroot}%{_sysconfdir}/profile.d
# Install profile links to override environment-modules
ln -s %{_datadir}/lmod/lmod/init/bash %{buildroot}%{_sysconfdir}/profile.d/modules.sh
ln -s %{_datadir}/lmod/lmod/init/csh %{buildroot}%{_sysconfdir}/profile.d/modules.csh
# Install the rpm config file
install -Dpm 644 %{SOURCE1} %{buildroot}/%{macrosdir}/macros.%{name}
# Override SitePackage.lua
install -Dpm 644 %{SOURCE2} %{buildroot}%{_datadir}/lmod/%{version}/libexec
# install icinga/nagios wrapper for the cache creation
install -Dpm 755 %{SOURCE3} %{buildroot}%{_datadir}/lmod/%{version}/libexec
# install admin.list
mkdir -p %{buildroot}%{_datadir}/lmod/etc
install -Dpm 644 %{SOURCE4} %{buildroot}%{_datadir}/lmod/etc

%clean
rm -rf %{buildroot}

%files
%doc INSTALL License README.md README_lua_modulefiles.txt
%{_sysconfdir}/modulefiles
%{_sysconfdir}/profile.d/modules.csh
%{_sysconfdir}/profile.d/modules.sh
%{_datadir}/lmod
%{_datadir}/modulefiles
%{macrosdir}/macros.%{name}


%changelog

* Thu Apr  2 2020 Franky Backeljauw <franky.backeljauw@uantwerpen.be> - 8.3.6-1.ua
- update to Lmod 8.3.6

* Wed Oct 16 2019 Franky Backeljauw <franky.backeljauw@uantwerpen.be> - 8.1.18-1.ua
- update to Lmod 8.1.18

* Mon Mar 11 2019 Franky Backeljauw <franky.backeljauw@uantwerpen.be> - 7.8.22-1.ua
- update to Lmod 7.8.22
- changed site name from "HPC-UAntwerpen" to "CalcUA"

* Wed Apr 4 2018 Kenneth Hoste <kenneth.hoste@ugent.be> - 7.7.26-1.ug
- update to Lmod 7.7.26 (clean error when cache file can not be read & more)

* Wed Mar  7 2018 Franky Backeljauw <franky.backeljauw@uantwerpen.be> - 7.7.15-1.ua
- update to Lmod 7.7.15 (initial HPC-UAntwerpen release)

* Fri Sep 29 2017 Kenneth Hoste <kenneth.hoste@ugent.be> - 7.7.5-1.ug
- update to Lmod 7.7.5 (faster bash completion)

* Thu Jul 13 2017 Kenneth Hoste <kenneth.hoste@ugent.be> - 7.5.10-7.ug
- add patch to ensure Lmod cache is used when loading cluster modules which include prepend_path($MODULEPATH, ...)

* Fri Jul 7 2017 Kenneth Hoste <kenneth.hoste@ugent.be> - 7.5.10-6.ug
- fix grabbing $MODULEPATH root from Lmod config in run_lmod_cache.py, 'config' was renamed to 'configT' in Lmod 7

* Thu Jul 6 2017 Kenneth Hoste <kenneth.hoste@ugent.be> - 7.5.10-5.ug
- update to Lmod 7.5.10
- fix msg hooks in SitePackage.lua (thanks to Ward Poelmans)
- remove patch for 'module' and 'ml', no longer needed
- add patch to avoid listing hidden cluster modules in output of 'ml spider'

* Mon Nov 28 2016 Ward Poelmans <ward.poelmans@ugent.be> - 6.6-2ug
- Install a admin.list (aka nag file)

* Fri Oct 14 2016 Ward Poelmans <ward.poelmans@ugent.be> - 6.6-1ug
- Use the json config interface of Lmod in cache creation script

* Thu May 19 2016 Ward Poelmans <ward.poelmans@ugent.be> - 6.3.5-2ug
- Add icinga/nagios wrapper for cache creation script

* Wed May 11 2016 Ward Poelmans <ward.poelmans@ugent.be> - 6.3.3-1ug
- Sync to upstream Lmod version
- Drop zsh as build dep (we don't use it)

* Thu Feb 18 2016 Ward Poelmans <ward.poelmans@ugent.be> - 6.1.3-1ug
- Adapt to UGent use

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 6.0.26-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Dec 22 2015 Orion Poplawski <orion@cora.nwra.com> - 6.0.24-2
- Add Requires: /usr/bin/ps

* Wed Oct 28 2015 Orion Poplawski <orion@cora.nwra.com> - 6.0.15-2
- Set PS path
- Add BR zsh

* Wed Oct 21 2015 Orion Poplawski <orion@cora.nwra.com> - 6.0.12-2
- Mark 00-modulepath files as config

* Mon Oct 19 2015 Orion Poplawski <orion@cora.nwra.com> - 6.0.12-1
- Drop shell patch fixed upstream

* Mon Oct 19 2015 Orion Poplawski <orion@cora.nwra.com> - 6.0.11-2
- Add patch to support generic and non-bash shells

* Tue Jul 14 2015 Orion Poplawski <orion@cora.nwra.com> - 6.0.5-1
- Drop tput patch applied upstream

* Thu Jul 9 2015 Orion Poplawski <orion@cora.nwra.com> - 5.9.4.2-4
- Add patch to suppress tput output

* Tue Jun 16 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.9.4.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue May 26 2015 Orion Poplawski <orion@cora.nwra.com> - 5.9.4.2-2
- Fix alternatives script handling

* Fri Jun 06 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri May 2 2014 Orion Poplawski <orion@cora.nwra.com> - 5.5-2
- Add EL support

* Tue Apr  1 2014 Orion Poplawski <orion@cora.nwra.com> - 5.3.2-1
- Initial package
