import os
from datetime import datetime

from PyQt5.QtWidgets import QSpinBox

from libmesact import mdi

def build(parent):
	buildErrors = []
	iniFilePath = os.path.join(parent.configPath, parent.configNameUnderscored + '.ini')
	parent.info_pte.appendPlainText(f'Building {iniFilePath}')

	iniContents = ['# This file was created with the Mesa Configuration Tool on ']
	iniContents.append(datetime.now().strftime('%b %d %Y %H:%M:%S') + '\n')
	iniContents.append('# Changes to most things are ok and will be read by the Configuration Tool\n')

	# build the [MESA] section
	iniContents.append('\n[MESA]\n')
	iniContents.append(f'VERSION = {parent.version}\n')

	'''
	board_names = {'7i92t': '7i92', '7i95t': '7i95'}
	if parent.boardCB.currentData() in board_names:
		board = board_names[parent.boardCB.currentData()]
	else:
		board = parent.boardCB.currentData()
	'''
	iniContents.append(f'BOARD = {parent.hal_name}\n')
	iniContents.append(f'BOARD_NAME = {parent.boardCB.currentText()}\n')
	if parent.firmwareCB.currentData():
		iniContents.append(f'FIRMWARE = {parent.firmwareCB.currentData()}\n')
	if parent.daughterCB_0.currentData() != None:
		iniContents.append(f'CARD_0 = {parent.daughterCB_0.currentData()}\n')
	if parent.daughterCB_1.currentData() != None:
		iniContents.append(f'CARD_1 = {parent.daughterCB_1.currentData()}\n')
	# build the [EMC] section
	iniContents.append('\n[EMC]\n')
	iniContents.append(f'VERSION = {parent.emcVersion}\n')
	iniContents.append(f'MACHINE = {parent.configNameLE.text()}\n')
	iniContents.append(f'DEBUG = {parent.debugCB.currentData()}\n')

	# build the [HM2] section
	iniContents.append('\n[HM2]\n')
	if parent.boardType == 'eth':
		iniContents.append('DRIVER = hm2_eth\n')
		iniContents.append(f'ADDRESS = {parent.ipAddressCB.currentText()}\n')
	elif parent.boardType == 'pci':
		iniContents.append('DRIVER = hm2_pci\n')
	elif parent.boardType == 'spi':
		iniContents.append('DRIVER = hm2_spix\n')

	#iniContents.append(f'STEPGENS = {parent.stepgens_cb.currentData()}\n')
	#iniContents.append(f'PWMGENS = {parent.pwmgens_cb.currentData()}\n')
	#iniContents.append(f'ENCODERS = {parent.encoders_cb.currentData()}\n')

	# build the [DISPLAY] section maxFeedOverrideLE
	iniContents.append('\n[DISPLAY]\n')
	if not parent.guiCB.currentData(): # use the user gui
		iniContents.append(f'DISPLAY = {parent.guiCB.currentText()}\n')
	else:
		iniContents.append(f'DISPLAY = {parent.guiCB.currentData()}\n')
	#iniContents.append(f'DISPLAY = {parent.guiCB.itemData(parent.guiCB.currentIndex())}\n')

	# Flex GUI
	if len(parent.flex_gui_le.text()) > 0:
		iniContents.append(f'GUI = {parent.flex_gui_le.text()}\n')
	if parent.keyboard_qss_cb.isChecked():
		iniContents.append(f'INPUT = keyboard\n')
	elif parent.touch_qss_cb.isChecked():
		iniContents.append(f'INPUT = touch\n')
	elif len(parent.custom_qss_le.text()) > 0:
		iniContents.append(f'QSS = {parent.custom_qss_le.text()}\n')
	if parent.flex_size_cb.currentData():
		iniContents.append(f'SIZE = {parent.flex_size_cb.currentData()}\n')

	if parent.editorCB.currentData():
		iniContents.append(f'EDITOR = {parent.editorCB.currentData()}\n')
	iniContents.append(f'PROGRAM_PREFIX = {os.path.expanduser("~/linuxcnc/nc_files")}\n')
	iniContents.append(f'POSITION_OFFSET = {parent.positionOffsetCB.currentData()}\n')
	iniContents.append(f'POSITION_FEEDBACK = {parent.positionFeedbackCB.currentData()}\n')
	iniContents.append(f'MAX_FEED_OVERRIDE = {parent.maxFeedOverrideSB.value():.1f}\n')
	if set('XYZUVW')&set(parent.coordinatesLB.text()):
		iniContents.append(f'MIN_LINEAR_VELOCITY = {parent.minLinJogVelDSB.value():.1f}\n')
		iniContents.append(f'DEFAULT_LINEAR_VELOCITY = {parent.defLinJogVelDSB.value():.1f}\n')
		iniContents.append(f'MAX_LINEAR_VELOCITY = {parent.maxLinJogVelDSB.value():.1f}\n')
	if set('ABC')&set(parent.coordinatesLB.text()):
		iniContents.append(f'MIN_ANGULAR_VELOCITY = {parent.minAngJogVelDSB.value():.1f}\n')
		iniContents.append(f'DEFAULT_ANGULAR_VELOCITY = {parent.defAngJogVelDSB.value():.1f}\n')
		iniContents.append(f'MAX_ANGULAR_VELOCITY = {parent.maxAngJogVelDSB.value():.1f}\n')
	if parent.jog_increments.text():
		iniContents.append(f'INCREMENTS = {parent.jog_increments.text()}\n')
	iniContents.append('CYCLE_TIME = 0.1\n')
	iniContents.append(f'INTRO_GRAPHIC = {parent.introGraphicLE.text()}\n')
	iniContents.append(f'INTRO_TIME = {parent.splashScreenSB.value()}\n')
	iniContents.append('OPEN_FILE = ""\n')
	if parent.pyvcpCB.isChecked():
		iniContents.append(f'PYVCP = {parent.configNameUnderscored}.xml\n')
	if parent.frontToolLatheRB.isChecked():
		iniContents.append('LATHE = 1\n')
	if parent.backToolLatheRB.isChecked():
		iniContents.append('BACK_TOOL_LATHE = 1\n')
	if parent.foamRB.isChecked():
		iniContents.append(f'Geometry = {parent.coordinatesLB.text()[0:2]};{parent.coordinatesLB.text()[2:4]}\n')
		iniContents.append('FOAM = 1\n')

	# build the [FILTER] section
	ext_list = []
	for i in range(3):
		ext = getattr(parent, f'filterExtLE_{i}').text()
		if ext:
			if not ext.startswith('.'):
				ext_list.append(f'.{ext}')
			else:
				ext_list.append(ext)
	if ext_list:
		iniContents.append('\n[FILTER]\n')
		iniContents.append(f'PROGRAM_EXTENSION = {", ".join(ext_list)} # G code Files\n')

	# build the [KINS] section
	iniContents.append('\n[KINS]\n')
	if len(set(parent.coordinatesLB.text())) == len(parent.coordinatesLB.text()): # 1 joint for each axis
		iniContents.append(f'KINEMATICS = trivkins coordinates={parent.coordinatesLB.text()}\n')
	else: # more than one joint per axis
		iniContents.append(f'KINEMATICS = trivkins coordinates={parent.coordinatesLB.text()} kinstype=BOTH\n')
	iniContents.append(f'JOINTS = {len(parent.coordinatesLB.text())}\n')

	# build the [EMCIO] section
	iniContents.append('\n[EMCIO]\n')
	iniContents.append('EMCIO = iov2\n')
	iniContents.append('CYCLE_TIME = 0.100\n')
	iniContents.append('TOOL_TABLE = tool.tbl\n')

	# build the [RS274NGC] section
	iniContents.append('\n[RS274NGC]\n')
	iniContents.append(f'PARAMETER_FILE = parameters.var\n')
	if parent.subroutineCB.isChecked():
		iniContents.append(f'SUBROUTINE_PATH = {os.path.expanduser("~/linuxcnc/subroutines")}\n')

	# build the [EMCMOT] section
	iniContents.append('\n[EMCMOT]\n')
	iniContents.append('EMCMOT = motmod\n')
	iniContents.append('COMM_TIMEOUT = 1.0\n')
	iniContents.append(f'SERVO_PERIOD = {parent.servoPeriodSB.value()}\n')

	# build the [TASK] section
	iniContents.append('\n[TASK]\n')
	iniContents.append('TASK = milltask\n')
	iniContents.append('CYCLE_TIME = 0.010\n')

	# build the [TRAJ] section
	iniContents.append('\n[TRAJ]\n')
	iniContents.append(f'COORDINATES = {parent.coordinatesLB.text()}\n')
	iniContents.append(f'LINEAR_UNITS = {parent.linearUnitsCB.currentData()}\n')
	iniContents.append('ANGULAR_UNITS = degree\n')
	iniContents.append(f'MAX_LINEAR_VELOCITY = {parent.trajMaxLinVelDSB.value():.1f}\n')
	if parent.noforcehomingCB.isChecked():
		iniContents.append(f'NO_FORCE_HOMING = 0\n')
	else:
		iniContents.append(f'NO_FORCE_HOMING = 1\n')

	# build the [HAL] section
	iniContents.append('\n[HAL]\n')
	iniContents.append(f'HALFILE = main.hal\n')
	iniContents.append('HALFILE = io.hal\n')
	if parent.ssCardCB.currentData():
		iniContents.append('HALFILE = sserial.hal\n')
	if parent.customhalCB.isChecked():
		iniContents.append('HALFILE = custom.hal\n')
	if parent.postguiCB.isChecked():
		iniContents.append('POSTGUI_HALFILE = postgui.hal\n')
	if parent.shutdownCB.isChecked():
		iniContents.append('SHUTDOWN = shutdown.hal\n')
	if parent.haluiCB.isChecked():
		iniContents.append('HALUI = halui\n')

	# build the [HALUI] section
	if parent.haluiCB.isChecked():
		iniContents.append('\n[HALUI]\n')
		for i in range(mdi.get_mdi_commands_count(parent)):
			cmd = mdi.get_mdi_command(parent, i)
			if cmd:
				iniContents.append(f'MDI_COMMAND = {cmd}\n')

	# build the axes and joints
	axes = [] # use only one axis letter with multiple joint axis
	joint = 0
	for i in range(3):
		for j in range(6):
			if getattr(parent, f'c{i}_axis_{j}').currentData():
				axis = getattr(parent, f'c{i}_axis_{j}').currentData()
				if axis and axis not in axes: # new axis
					axes.append(axis)
					iniContents.append(f'\n[AXIS_{axis}]\n')
					iniContents.append(f'MIN_LIMIT = {getattr(parent, f"c{i}_min_limit_{j}").text()}\n')
					iniContents.append(f'MAX_LIMIT = {getattr(parent, f"c{i}_max_limit_{j}").text()}\n')
					iniContents.append(f'MAX_VELOCITY = {getattr(parent, f"c{i}_max_vel_{j}").text()}\n')
					iniContents.append(f'MAX_ACCELERATION = {getattr(parent, f"c{i}_max_accel_{j}").text()}\n')
				iniContents.append(f'\n[JOINT_{joint}]\n')
				iniContents.append(f'CARD = {i}\n')
				iniContents.append(f'TAB = {j}\n')
				iniContents.append(f'AXIS = {getattr(parent, f"c{i}_axis_{j}").currentData()}\n')
				iniContents.append(f'MIN_LIMIT = {getattr(parent, f"c{i}_min_limit_{j}").text()}\n')
				iniContents.append(f'MAX_LIMIT = {getattr(parent, f"c{i}_max_limit_{j}").text()}\n')
				iniContents.append(f'MAX_VELOCITY = {getattr(parent, f"c{i}_max_vel_{j}").text()}\n')
				iniContents.append(f'MAX_ACCELERATION = {getattr(parent, f"c{i}_max_accel_{j}").text()}\n')
				iniContents.append(f'TYPE = {getattr(parent, f"c{i}_axisType_{j}").text()}\n')

				if getattr(parent, f'c{i}_scale_{j}').isEnabled():
					iniContents.append(f'SCALE = {getattr(parent, f"c{i}_scale_{j}").text()}\n')

				if getattr(parent, f'c{i}_settings_{j}').isTabVisible(2): # Stepgen Tab
					iniContents.append(f'DRIVE = {getattr(parent, f"c{i}_drive_{j}").currentText()}\n')
					iniContents.append(f'STEP_INVERT = {getattr(parent, f"c{i}_StepInvert_{j}").isChecked()}\n')
					iniContents.append(f'DIR_INVERT = {getattr(parent, f"c{i}_DirInvert_{j}").isChecked()}\n')
					iniContents.append(f'STEPGEN_MAX_VEL = {float(getattr(parent, f"c{i}_max_vel_{j}").text()) * 1.2:.2f}\n')
					iniContents.append(f'STEPGEN_MAX_ACC = {float(getattr(parent, f"c{i}_max_accel_{j}").text()) * 1.2:.2f}\n')
					iniContents.append(f'DIRSETUP = {getattr(parent, f"c{i}_DirSetup_{j}").text()}\n')
					iniContents.append(f'DIRHOLD = {getattr(parent, f"c{i}_DirHold_{j}").text()}\n')
					iniContents.append(f'STEPLEN = {getattr(parent, f"c{i}_StepTime_{j}").text()}\n')
					iniContents.append(f'STEPSPACE = {getattr(parent, f"c{i}_StepSpace_{j}").text()}\n')

				if getattr(parent, f'c{i}_settings_{j}').isTabVisible(3): # Analog Tab
					iniContents.append(f'ANALOG_SCALE_MAX = {getattr(parent, f"c{i}_analogScaleMax_{j}").text()}\n')
					iniContents.append(f'ANALOG_MIN_LIMIT = {getattr(parent, f"c{i}_analogMinLimit_{j}").text()}\n')
					iniContents.append(f'ANALOG_MAX_LIMIT = {getattr(parent, f"c{i}_analogMaxLimit_{j}").text()}\n')

				if getattr(parent, f'c{i}_settings_{j}').isTabVisible(4): # Encoder Tab
					iniContents.append(f'ENCODER_SCALE = {getattr(parent, f"c{i}_encoderScale_{j}").text()}\n')

				iniContents.append(f'FERROR = {getattr(parent, f"c{i}_max_ferror_{j}").text()}\n')
				iniContents.append(f'MIN_FERROR = {getattr(parent, f"c{i}_min_ferror_{j}").text()}\n')
				iniContents.append(f'DEADBAND = {getattr(parent, f"c{i}_deadband_{j}").text()}\n')
				iniContents.append(f'P = {getattr(parent, f"c{i}_p_{j}").text()}\n')
				iniContents.append(f'I = {getattr(parent, f"c{i}_i_{j}").text()}\n')
				iniContents.append(f'D = {getattr(parent, f"c{i}_d_{j}").text()}\n')
				iniContents.append(f'FF0 = {getattr(parent, f"c{i}_ff0_{j}").text()}\n')
				iniContents.append(f'FF1 = {getattr(parent, f"c{i}_ff1_{j}").text()}\n')
				iniContents.append(f'FF2 = {getattr(parent, f"c{i}_ff2_{j}").text()}\n')
				iniContents.append(f'BIAS = {getattr(parent, f"c{i}_bias_{j}").text()}\n')
				iniContents.append(f'MAX_OUTPUT = {getattr(parent, f"c{i}_maxOutput_{j}").text()}\n')
				iniContents.append(f'MAX_ERROR = {getattr(parent, f"c{i}_maxError_{j}").text()}\n')

				if getattr(parent, f"c{i}_home_{j}").text():
					iniContents.append(f'HOME = {getattr(parent, f"c{i}_home_{j}").text()}\n')
				if getattr(parent, f"c{i}_homeOffset_{j}").text():
					iniContents.append(f'HOME_OFFSET = {getattr(parent, f"c{i}_homeOffset_{j}").text()}\n')
				if getattr(parent, f"c{i}_homeSearchVel_{j}").text():
					iniContents.append(f'HOME_SEARCH_VEL = {getattr(parent, f"c{i}_homeSearchVel_{j}").text()}\n')
				if getattr(parent, f"c{i}_homeLatchVel_{j}").text():
					iniContents.append(f'HOME_LATCH_VEL = {getattr(parent, f"c{i}_homeLatchVel_{j}").text()}\n')
				if getattr(parent, f"c{i}_homeFinalVelocity_{j}").text():
					iniContents.append(f'HOME_FINAL_VEL = {getattr(parent, f"c{i}_homeFinalVelocity_{j}").text()}\n')
				if getattr(parent, f"c{i}_homeSequence_{j}").text():
					iniContents.append(f'HOME_SEQUENCE = {getattr(parent, f"c{i}_homeSequence_{j}").text()}\n')
				if getattr(parent, f"c{i}_homeIgnoreLimits_{j}").isChecked():
					iniContents.append(f'HOME_IGNORE_LIMITS = {getattr(parent, f"c{i}_homeIgnoreLimits_{j}").isChecked()}\n')
				if getattr(parent, f"c{i}_homeUseIndex_{j}").isChecked():
					iniContents.append(f'HOME_USE_INDEX = {getattr(parent, f"c{i}_homeUseIndex_{j}").isChecked()}\n')
				if getattr(parent, f"c{i}_homeSwitchShared_{j}").isChecked():
					iniContents.append(f'HOME_IS_SHARED = {getattr(parent, f"c{i}_homeSwitchShared_{j}").isChecked()}\n')
				joint += 1

	# build the [SPINDLE] section if enabled
	'''
	pwm_7i96s_sb
	max_rpm_7i96s_sb
	Note
	These settings are for the motion controller component. Control screens can
	limit these settings further.

	MAX_FORWARD_VELOCITY = 20000 The maximum spindle speed (in rpm) for the
	specified spindle. Optional. This will also set MAX_REVERSE_VELOCITY to the
	negative value unless overridden.

	MIN_FORWARD_VELOCITY = 3000 The minimum spindle speed (in rpm) for the
	specified spindle. Optional. Many spindles have a minimum speed below which
	they should not be run. Any spindle speed command below this limit will be
	/increased/ to this limit.

	MAX_REVERSE_VELOCITY = 20000 This setting will default to MAX_FORWARD_VELOCITY
	if omitted. It can be used in cases where the spindle speed is limited in
	reverse. Set to zero for spindles which must not be run in reverse. In this
	context "max" refers to the absolute magnitude of the spindle speed.

	MIN_REVERSE_VELOCITY = 3000` This setting is equivalent to
	MIN_FORWARD_VELOCITY but for reverse spindle rotation. It will default to the
	MIN_FORWARD_VELOCITY if omitted.

	spindle_fwd_min_rpm
	spindle_fwd_max_rpm
	spindle_rev_min_rpm
	spindle_rev_max_rpm

	'''
	if parent.spindle_enable_cb.isChecked():
		iniContents.append('\n[SPINDLE_0]\n')
		if parent.board_name == '7i96S':
			iniContents.append(f'PWM_TYPE = 1\n')
			iniContents.append(f'PWM_FREQUENCY = 20000\n')

		iniContents.append(f'P = {parent.p_s.value():.1f}\n')
		iniContents.append(f'I = {parent.i_s.value():.1f}\n')
		iniContents.append(f'D = {parent.d_s.value():.1f}\n')
		iniContents.append(f'FF0 = {parent.ff0_s.value():.1f}\n')
		iniContents.append(f'FF1 = {parent.ff1_s.value():.1f}\n')
		iniContents.append(f'FF2 = {parent.ff2_s.value():.1f}\n')
		iniContents.append(f'BIAS = {parent.bias_s.value():.1f}\n')
		iniContents.append(f'DEADBAND = {parent.deadband_s.value():.1f}\n')

		if parent.hal_name == '5i25': 
			if parent.connector_7i76_cb.currentData():
				iniContents.append(f'MAX_OUTPUT = {parent.max_rpm_7i76_sb.value()}\n')
				iniContents.append(f'SCALE_MAX = {parent.max_scale_7i76_sb.value()}\n')
				iniContents.append(f'CONNECTOR = {parent.connector_7i76_cb.currentText()}\n')

		elif parent.hal_name == '7i92':
			if parent.connector_7i76_cb.currentData():
				iniContents.append(f'MAX_OUTPUT = {parent.max_rpm_7i76_sb.value()}\n')
				iniContents.append(f'SCALE_MAX = {parent.max_scale_7i76_sb.value()}\n')
				iniContents.append(f'CONNECTOR = {parent.connector_7i76_cb.currentText()}\n')

		elif parent.board_name == '7i76E':
			iniContents.append(f'MAX_OUTPUT = {parent.max_rpm_7i76e_sb.value()}\n')
			iniContents.append(f'SCALE_MAX = {parent.max_scale_7i76e_sb.value()}\n')
		elif parent.board_name == '7i76EU':
			iniContents.append(f'MAX_OUTPUT = {parent.max_rpm_7i76eu_sb.value()}\n')
			iniContents.append(f'SCALE_MAX = {parent.max_scale_7i76eu_sb.value()}\n')
		elif parent.board_name == '7i96S':
			iniContents.append(f'MAX_OUTPUT = {parent.max_rpm_7i96s_sb.value()}\n')

		if parent.emc_version >= (2, 9, 1):
			if parent.spindle_min_fwd_enable_cb.isChecked():
				iniContents.append(f'MIN_FORWARD_VELOCITY = {parent.spindle_fwd_min_rpm.value()}\n')
			if parent.spindle_max_fwd_enable_cb.isChecked():
				iniContents.append(f'MAX_FORWARD_VELOCITY = {parent.spindle_fwd_max_rpm.value()}\n')
			if parent.spindle_min_rev_enable_cb.isChecked():
					iniContents.append(f'MIN_REVERSE_VELOCITY = {parent.spindle_rev_min_rpm.value()}\n')
			if parent.spindle_max_rev_enable_cb.isChecked():
					iniContents.append(f'MAX_REVERSE_VELOCITY = {parent.spindle_rev_max_rpm.value()}\n')

		'''
		if parent.spindleTypeCB.currentData() == 'pwm':
			iniContents.append(f'PWM_TYPE = 1\n')
			iniContents.append(f'PWM_FREQUENCY = {parent.pwmFrequencySB.value()}\n')
			iniContents.append(f'MAX_ERROR = {parent.maxError_s.value():.1f}\n')

			iniContents.append(f'MIN_FORWARD_VELOCITY = {parent.spindleMinRpmFwd.value()}\n')
			iniContents.append(f'MAX_FORWARD_VELOCITY = {parent.spindleMaxRpmFwd.value()}\n')
			iniContents.append(f'MIN_REVERSE_VELOCITY = {parent.spindleMinRpmRev.value()}\n')
			iniContents.append(f'MAX_REVERSE_VELOCITY = {parent.spindleMaxRpmRev.value()}\n')
		'''

		if parent.spindleFeedbackCB.currentData() == 'encoder':
			iniContents.append(f'FEEDBACK = {parent.spindleFeedbackCB.currentData()}\n')
			iniContents.append(f'SCALE = {parent.spindleEncoderScale.value():.1f}\n')

		'''
		if parent.spindleTypeCB.currentData()[:7] == 'stepgen':
			iniContents.append(f'DRIVE = {parent.spindleDriveCB.currentText()}\n')
			iniContents.append(f'SCALE = {parent.spindleStepScale.text()}\n')
			iniContents.append(f'STEPLEN = {parent.spindleStepTime.text()}\n')
			iniContents.append(f'STEPSPACE = {parent.spindleStepSpace.text()}\n')
			iniContents.append(f'DIRSETUP = {parent.spindleDirSetup.text()}\n')
			iniContents.append(f'DIRHOLD = {parent.spindleDirHold.text()}\n')
			iniContents.append(f'STEP_INVERT = {parent.spindleStepInvert.isChecked()}\n')
			iniContents.append(f'DIR_INVERT = {parent.spindleDirInvert.isChecked()}\n')
			iniContents.append(f'MIN_RPM = {parent.spindleMinRpm.value()}\n')
			iniContents.append(f'MAX_RPM = {parent.spindleMaxRpm.value()}\n')
			iniContents.append(f'MIN_RPS = {parent.spindleMinRps.text()}\n')
			iniContents.append(f'MAX_RPS = {parent.spindleMaxRps.text()}\n')
			iniContents.append(f'MAX_ACCEL_RPM = {parent.spindleMaxAccel.value()}\n')
			iniContents.append(f'MAX_ACCEL_RPS = {parent.spindleMaxRpss.text()}\n')
		'''

	# 7i77 spindle c2_spindle_cb
	for i in range(1,3):
		if getattr(parent, f'c{i}_spindle_cb').isChecked():
			iniContents.append('\n[SPINDLE_7I77]\n')
			iniContents.append(f'CARD = {i}\n')
			iniContents.append(f'P = {getattr(parent, f"c{i}_p_5").text()}\n')
			iniContents.append(f'I = {getattr(parent, f"c{i}_i_5").text()}\n')
			iniContents.append(f'D = {getattr(parent, f"c{i}_d_5").text()}\n')
			iniContents.append(f'FF0 = {getattr(parent, f"c{i}_ff0_5").text()}\n')
			iniContents.append(f'FF1 = {getattr(parent, f"c{i}_ff1_5").text()}\n')
			iniContents.append(f'FF2 = {getattr(parent, f"c{i}_ff2_5").text()}\n')
			iniContents.append(f'BIAS = {getattr(parent, f"c{i}_bias_5").text()}\n')
			iniContents.append(f'DEADBAND = {getattr(parent, f"c{i}_deadband_5").text()}\n')
			iniContents.append(f'MIN_RPM = {getattr(parent, f"c{i}_analogMinLimit_5").text()}\n')
			iniContents.append(f'MAX_RPM = {getattr(parent, f"c{i}_analogMaxLimit_5").text()}\n')
			iniContents.append(f'SCALE_MAX = {getattr(parent, f"c{i}_analogScaleMax_5").text()}\n')

	# build the [INPUTS] section from pushbuttons
	iniContents.append('\n[INPUTS]\n')
	iniContents.append('# DO NOT change the inputs they are used by the configuration tool\n')
	for i in range(3):
		if parent.mainTW.isTabVisible(i + 3): # if the board tab is visible
			if getattr(parent, f'c{i}_JointTW').isTabVisible(1):
				for j in range(32):
					if getattr(parent, f"c{i}_input_{j}").text() != 'Select': # only add inputs that are used
						iniContents.append(f'INPUT_{i}_{j} = {getattr(parent, f"c{i}_input_{j}").text()}\n')
						iniContents.append(f'INPUT_INVERT_{i}_{j} = {getattr(parent, f"c{i}_input_invert_{j}").isChecked()}\n')
						iniContents.append(f'INPUT_SLOW_{i}_{j} = {getattr(parent, f"c{i}_input_debounce_{j}").isChecked()}\n')

	# build the [OUTPUTS] section from pushbuttons
	iniContents.append('\n[OUTPUTS]\n')
	iniContents.append('# DO NOT change the outputs they are used by the configuration tool\n')
	sink = ''
	source = ''
	if parent.boardCB.currentText() == '7i76EU':
		for i in range(16):
			sink += getattr(parent, f'c0_output_type_{i}').currentData()[0]
			source += getattr(parent, f'c0_output_type_{i}').currentData()[1]
		iniContents.append(f'OUTPUT_SINK = {sink}\n')
		iniContents.append(f'OUTPUT_SOURCE = {source}\n')

	for i in range(3):
		if parent.mainTW.isTabVisible(i + 3): # if the board tab is visible
			index = getattr(parent, f'c{i}_JointTW').indexOf(getattr(parent, f'c{i}_outputs'))
			if getattr(parent, f'c{i}_JointTW').isTabVisible(index): # if the outputs tab is visible
				for j in range(16):
					if getattr(parent, f"c{i}_output_{j}").text() != 'Select': # only add outputs that are used
						iniContents.append(f'OUTPUT_{i}_{j} = {getattr(parent, f"c{i}_output_{j}").text()}\n')
						iniContents.append(f'OUTPUT_INVERT_{i}_{j} = {getattr(parent, f"c{i}_output_invert_{j}").isChecked()}\n')

	# build the [OPTIONS] section
	iniContents.append('\n[OPTIONS]\n')
	iniContents.append('# DO NOT change the options they are used by the configuration tool\n')
	iniContents.append(f'LOAD_CONFIG = {parent.load_config_cb.isChecked()}\n')
	iniContents.append(f'INTRO_GRAPHIC = {parent.introGraphicLE.text()}\n')
	iniContents.append(f'INTRO_GRAPHIC_TIME = {parent.splashScreenSB.value()}\n')
	iniContents.append(f'MANUAL_TOOL_CHANGE = {parent.manualToolChangeCB.isChecked()}\n')
	iniContents.append(f'CUSTOM_HAL = {parent.customhalCB.isChecked()}\n')
	iniContents.append(f'POST_GUI_HAL = {parent.postguiCB.isChecked()}\n')
	iniContents.append(f'SHUTDOWN_HAL = {parent.shutdownCB.isChecked()}\n')
	iniContents.append(f'HALUI = {parent.haluiCB.isChecked()}\n')
	iniContents.append(f'PYVCP = {parent.pyvcpCB.isChecked()}\n')
	iniContents.append(f'GLADEVCP = {parent.gladevcpCB.isChecked()}\n')
	iniContents.append(f'LADDER = {parent.ladderGB.isChecked()}\n')
	iniContents.append(f'BACKUP = {parent.backupCB.isChecked()}\n')

	# build the [PLC] section
	if parent.ladderGB.isChecked(): # check for any options
		iniContents.append('\n[PLC]\n')
		iniContents.append('# DO NOT change the plc options they are used by the configuration tool\n')
		children = parent.ladderGB.findChildren(QSpinBox)
		for child in children:
			iniContents.append(f'{getattr(parent, child.objectName()).property("item")} = {getattr(parent, child.objectName()).value()}\n')

	# build the [SSERIAL] section
	if parent.ssCardCB.currentData():
		iniContents.append('\n[SSERIAL]\n')
		iniContents.append('# DO NOT change the sserial they are used by the configuration tool\n')
		iniContents.append(f'SS_CARD = {parent.ssCardCB.currentText()}\n')
	if parent.ssCardCB.currentText() == '7i64':
		# 24 ss7i64in_
		# 24 ss7i64out_
		for i in range(24):
			if getattr(parent, f'ss7i64in_{i}').text() != 'Select':
				iniContents.append(f'ss7i64in_{i} = {getattr(parent, "ss7i64in_" + str(i)).text()}\n')
		for i in range(24):
			if getattr(parent, f'ss7i64out_{i}').text() != 'Select':
				iniContents.append(f'ss7i64out_{i} = {getattr(parent, "ss7i64out_" + str(i)).text()}\n')

	elif parent.ssCardCB.currentText() == '7i69':
		# 24 ss7i69in_
		# 24 ss7i69out_
		for i in range(24):
			if getattr(parent, f'ss7i69in_{i}').text() != 'Select':
				iniContents.append(f'ss7i69in_{i} = {getattr(parent, "ss7i69in_" + str(i)).text()}\n')
		for i in range(24):
			if getattr(parent, f'ss7i69out_{i}').text() != 'Select':
				iniContents.append(f'ss7i69out_{i} = {getattr(parent, "ss7i69out_" + str(i)).text()}\n')

	elif parent.ssCardCB.currentText() == '7i70':
		# 48 ss7i70in_
		for i in range(48):
			if getattr(parent, f'ss7i70in_{i}').text() != 'Select':
				iniContents.append(f'ss7i70in_{i} = {getattr(parent, "ss7i70in_" + str(i)).text()}\n')

	elif parent.ssCardCB.currentText() == '7i71':
		# 48 ss7i71out_
		for i in range(48):
			if getattr(parent, f'ss7i71out_{i}').text() != 'Select':
				iniContents.append(f'ss7i71out_{i} = {getattr(parent, "ss7i71out_" + str(i)).text()}\n')

	elif parent.ssCardCB.currentText() == '7i72':
		# 48 ss7i72out_
		for i in range(48):
			if getattr(parent, f'ss7i72out_{i}').text() != 'Select':
				iniContents.append(f'ss7i72out_{i} = {getattr(parent, "ss7i72out_" + str(i)).text()}\n')

	elif parent.ssCardCB.currentText() == '7i73':
		# 16 ss7i73key_
		# 12 ss7i73lcd_
		# 16 ss7i73in_
		# 2 ss7i73out_
		for i in range(16):
			if getattr(parent, f'ss7i73key_{i}').text() != 'Select':
				iniContents.append(f'ss7i73key_{i} = {getattr(parent, "ss7i73key_" + str(i)).text()}\n')
		for i in range(12):
			if getattr(parent, f'ss7i73lcd_{i}').text() != 'Select':
				iniContents.append(f'ss7i73lcd_{i} = {getattr(parent, "ss7i73lcd_" + str(i)).text()}\n')
		for i in range(16):
			if getattr(parent, f'ss7i73in_{i}').text() != 'Select':
				iniContents.append(f'ss7i73in_{i} = {getattr(parent, "ss7i73in_" + str(i)).text()}\n')
		for i in range(2):
			if getattr(parent, f'ss7i73out_{i}').text() != 'Select':
				iniContents.append(f'ss7i73out_{i} = {getattr(parent, "ss7i73out_" + str(i)).text()}\n')

	elif parent.ssCardCB.currentText() == '7i84':
		# 32 ss7i84in_
		# 16 ss7i84out_
		for i in range(32):
			if getattr(parent, f'ss7i84in_{i}').text() != 'Select':
				iniContents.append(f'ss7i84in_{i} = {getattr(parent, "ss7i84in_" + str(i)).text()}\n')
		for i in range(16):
			if getattr(parent, f'ss7i84out_{i}').text() != 'Select':
				iniContents.append(f'ss7i84out_{i} = {getattr(parent, "ss7i84out_" + str(i)).text()}\n')

	elif parent.ssCardCB.currentText() == '7i87':
		# 8 ss7i87in_
		for i in range(8):
			if getattr(parent, f'ss7i87in_{i}').text() != 'Select':
				iniContents.append(f'ss7i87in_{i} = {getattr(parent, "ss7i87in_" + str(i)).text()}\n')

	try:
		with open(iniFilePath, 'w') as iniFile:
			iniFile.writelines(iniContents)
	except OSError:
		parent.info_pte.appendPlainText(f'OS error\n {traceback.print_exc()}')
