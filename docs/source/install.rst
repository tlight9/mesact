==========
Installing
==========

Mesa Configuration Tool

.. Note:: Tested on Debian 10, 11, 12, 13 and Linux Mint 20.2 but it should work on
	other Debian type OS's.

.. Note:: Requires Python 3.6 or newer to work.

Use the Debian deb for installing the Mesa Configuration Tool!

Latest Version of the Mesa Configuration Tool is in the
`Releases <https://github.com/jethornton/mesact/releases>`_

Select the one that suits your OS.

Open the File Manager and right click on the file and open with Gdebi then install.

.. Warning:: The graphical Gdebi does not work on the LinuxCNC chosen desktop so
   you have to use the terminal to install a deb file.

If you don't have Gdebi installed you can install it from a terminal
::

	sudo apt install gdebi

If the graphical version of gdebi has problems you can run it from a
terminal in the directory where you downloaded the deb with n.n.n replaced
by the version your installing.
::

	sudo gdebi mesact_n.n.n_amd64.deb

If you don't have LinuxCNC installed then the mesact Configuration tool
will show up in the Applications > Other menu otherwise it will be in
the CNC menu.

If you have problems try running from a terminal with:
::

	mesact

To flash firmware to the mesact you need to install 
`mesaflash <https://github.com/LinuxCNC/mesaflash>`_ from the LinuxCNC
repository.

To uninstall the mesact Configuration Tool right click on the .deb file
and open with Gdebi and select `Remove Package`.

To check for newer versions Help > Check for Updates

To upgrade the mesact Configuration Tool delete the .deb file and download
a fresh copy then right click on the .deb file and open with Gdebi and
select `Reinstall Package`

