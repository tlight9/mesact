import os
from configparser import ConfigParser

from PyQt5.QtWidgets import (QFileDialog, QLabel, QLineEdit, QSpinBox,
	QDoubleSpinBox, QCheckBox, QGroupBox, QComboBox, QPushButton, QRadioButton)

from libmesact import utilities
from libmesact import dialogs
from libmesact import mdi
from libmesact import hal

class loadini:
	def __init__(self):
		super().__init__()
		self.sections = {}
		self.iniFile = ''
		self.iniUnknown = False

	def checkini(self, parent, configName = ''):
		parent.mainTW.setCurrentIndex(0)
		parent.info_pte.clear()
		if not configName: # open file dialog
			if os.path.isdir(os.path.expanduser('~/linuxcnc/configs')):
				configsDir = os.path.expanduser('~/linuxcnc/configs')
			else:
				configsDir = os.path.expanduser('~/')
			fileName = QFileDialog.getOpenFileName(parent,
			caption="Select Configuration INI File", directory=configsDir,
			filter='*.ini', options=QFileDialog.DontUseNativeDialog,)
			iniFile = fileName[0]
			base = os.path.basename(iniFile)
			configName = os.path.splitext(base)[0]
		else: # we passed a file name
			configName = configName.replace(' ','_').lower()
			configsDir = os.path.expanduser('~/linuxcnc/configs')
			iniFile = os.path.join(configsDir, configName, configName + '.ini')

			if not os.path.isfile(iniFile):
				msg = f'File {iniFile} not found'
				dialogs.errorMsgOk(msg, 'Not Found')
				return
		if iniFile:
			with open(iniFile) as f:
				line = f.readline()
				if 'PNCconf' in line:
					msg = (f'The ini file is created with PNCconf!\n'
						'The files will be saved to a zip file then\n'
						'the all the files in the directory will be DELETED\n'
						'Save a Backup and try and open the ini?')
					if dialogs.errorMsgCancelOk(msg, 'PNCconf File'):
						path, filename = os.path.split(iniFile)
						utilities.backupFiles(parent, path)
						utilities.cleanDir(parent, path)
						self.iniUnknown = True
					else:
						return
				elif 'Mesa' not in line:
					msg = (f'The ini file was not created\n'
						'with the Mesa Configuration Tool!\n'
						'The files will be saved to a zip file then\n'
						'the all the files in the directory will be DELETED\n'
						'Save a Backup and try and open the ini?')
					if dialogs.errorMsgCancelOk(msg, 'Unknown File'):
						path, filename = os.path.split(iniFile)
						utilities.backupFiles(parent, path)
						utilities.cleanDir(parent, path)
						self.iniUnknown = True
					else:
						return

			parent.info_pte.appendPlainText(f'Loading {iniFile}')
			self.load_ini(parent, iniFile)
			self.loadReadMe(parent, configName)
		else:
			parent.info_pte.appendPlainText('Open File Cancled')
			iniFile = ''

	def load_ini(self, parent, iniFile):
		utilities.new_config(parent)
		parent.loading = True
		iniDict = {}
		with open(iniFile,'r') as file:
			self.content = file.readlines() # create a list of the ini file
		self.get_sections()
		if '[MESA]' in self.sections:
			start = self.sections['[MESA]'][0]
			end = self.sections['[MESA]'][1]
			for line in self.content[start:end]:
				if line.startswith('VERSION'):
					if '=' in line:
						key, value = line.split('=')
						ini_version = tuple(map(int,value.strip().split('.')))
						tool_version = tuple(map(int, parent.version.split('.')))
						if ini_version < tool_version:
							msg = (f'The ini file version is {value.strip()}\n'
								f'The Configuration Tool version is {parent.version}\n'
								'The ini file will be saved to a zip file then deleted\n'
								'Save a Backup and try and open the ini?')
							if dialogs.errorMsgCancelOk(msg, 'Version Difference'):
								path, filename = os.path.split(iniFile)
								utilities.backupFiles(parent, path)
								#utilities.cleanDir(parent, path)
								utilities.file_delete(parent, iniFile)
							else:
								return

		# pncconf try and figure out what card and address
		if '[HMOT]' in self.sections:
			start = self.sections['[HMOT]'][0]
			end = self.sections['[HMOT]'][1]
			for item in self.content[start:end]:
				if item.startswith('CARD0'):
					if '=' in item:
						key, value = item.split('=')
						start = value.find('_') + 1
						end = value.find('.')
						data = value[start:end]
						if parent.boardCB.findData(data) >= 0:
							parent.boardCB.setCurrentIndex(parent.boardCB.findData(data))

		mesa = []
		mesa.append(['[MESA]', 'BOARD_NAME', 'boardCB'])
		mesa.append(['[MESA]', 'FIRMWARE', 'firmwareCB'])
		mesa.append(['[MESA]', 'CARD_0', 'daughterCB_0'])
		mesa.append(['[MESA]', 'CARD_1', 'daughterCB_1'])
		mesa.append(['[MESA]', 'CARD_2', 'daughterCB_2'])

		for item in mesa:
			self.update(parent, item[0], item[1], item[2])

		emc = [
		['[EMC]', 'MACHINE', 'configNameLE'],
		['[EMC]', 'DEBUG', 'debugCB']
		]
		for item in emc:
			self.update(parent, item[0], item[1], item[2])

		hm2 = [
		['[HM2]', 'ADDRESS', 'ipAddressCB'],
		['[HM2]', 'STEPGENS', 'stepgens_cb'],
		['[HM2]', 'PWMGENS', 'pwmgens_cb'],
		['[HM2]', 'ENCODERS', 'encoders_cb']
		]
		for item in hm2:
			self.update(parent, item[0], item[1], item[2])

		if '[DISPLAY]' in self.sections: # allow custom gui
			start = self.sections['[DISPLAY]'][0]
			end = self.sections['[DISPLAY]'][1]
			for item in self.content[start:end]:
				item = item.strip() # remove newline
				if '=' in item:
					key, value = item.replace(' ', '').split('=') # remove spaces and split
					if key == 'DISPLAY':
						index = parent.guiCB.findData(value)
						if index > 0:
							parent.guiCB.setCurrentIndex(index)
						else:
							parent.guiCB.setItemText(0, value)
					if key == 'INPUT':
						if value == 'keyboard':
							parent.keyboard_qss_cb.setChecked(True)
						elif value == 'touch':
							parent.touch_qss_cb.setChecked(True)

		display = [
		['[DISPLAY]', 'EDITOR', 'editorCB'],
		['[DISPLAY]', 'POSITION_OFFSET', 'positionOffsetCB'],
		['[DISPLAY]', 'POSITION_FEEDBACK', 'positionFeedbackCB'],
		['[DISPLAY]', 'MAX_FEED_OVERRIDE', 'maxFeedOverrideSB'],
		['[DISPLAY]', 'MIN_VELOCITY', 'minLinJogVelDSB'],
		['[DISPLAY]', 'DEFAULT_LINEAR_VELOCITY', 'defLinJogVelDSB'],
		['[DISPLAY]', 'MAX_LINEAR_VELOCITY', 'maxLinJogVelDSB'],
		['[DISPLAY]', 'MIN_ANGULAR_VELOCITY', 'minAngJogVelDSB'],
		['[DISPLAY]', 'DEFAULT_ANGULAR_VELOCITY', 'defAngJogVelDSB'],
		['[DISPLAY]', 'MAX_ANGULAR_VELOCITY', 'maxAngJogVelDSB'],
		['[DISPLAY]', 'INCREMENTS', 'jog_increments'],
		['[DISPLAY]', 'LATHE', 'frontToolLatheRB'],
		['[DISPLAY]', 'BACK_TOOL_LATHE', 'backToolLatheRB'],
		['[DISPLAY]', 'FOAM', 'foamRB'],
		['[DISPLAY]', 'GUI', 'flex_gui_le'],
		['[DISPLAY]', 'QSS', 'custom_qss_le'],
		['[DISPLAY]', 'SIZE', 'flex_size_cb'],
		]

		for item in display:
			self.update(parent, item[0], item[1], item[2])

		if '[FILTER]' in self.sections:
			start = self.sections['[FILTER]'][0]
			end = self.sections['[FILTER]'][1]
			for item in self.content[start:end]:
				if 'G code Files' in item:
					extList = []
					for word in item.split():
						if word.startswith('.'):
							extList.append(word.rstrip(','))
					for i, item in enumerate(extList):
						getattr(parent, f'filterExtLE_{i}').setText(item)
					break

		self.update(parent, '[EMCMOT]', 'SERVO_PERIOD', 'servoPeriodSB')

		traj = [
		['[TRAJ]', 'LINEAR_UNITS', 'linearUnitsCB'],
		['[TRAJ]', 'MAX_LINEAR_VELOCITY', 'trajMaxLinVelDSB'],
		]

		for item in traj:
			self.update(parent, item[0], item[1], item[2])

		if '[HALUI]' in self.sections:
			start = self.sections['[HALUI]'][0]
			end = self.sections['[HALUI]'][1]
			mdicmd = []
			mdi.cleanup_mdi_commands(parent)
			for item in self.content[start:end]:
				if item != '\n' and item.startswith('MDI_COMMAND'):
					if '=' in item:
						item = item.split('=')
						item = item[1].strip()
						mdicmd.append(item)
			for i, item in enumerate(mdicmd):
				mdi.set_mdi_command(parent, i, item)

		for section in self.sections.items():
			if section[0].startswith('[JOINT'):
				joint = section[0][-2].strip()
				card = 0
				tab = 0
				start = section[1][0]
				end = section[1][1]
				for i in range(start, end):
					item = self.content[i].strip()
					if item.startswith('CARD'):
						if '=' in item:
							card = item.split('=')[1].strip()
					elif item.startswith('TAB'):
						if '=' in item:
							tab = item.split('=')[1].strip()
				joint_list = [
				[f'[JOINT_{joint}]', 'AXIS', f'c{card}_axis_{tab}'],
				[f'[JOINT_{joint}]', 'DRIVE', f'c{card}_drive_{tab}'],
				[f'[JOINT_{joint}]', 'STEP_INVERT', f'c{card}_StepInvert_{tab}'],
				[f'[JOINT_{joint}]', 'DIR_INVERT', f'c{card}_DirInvert_{tab}'],
				[f'[JOINT_{joint}]', 'STEPLEN', f'c{card}_StepTime_{tab}'],
				[f'[JOINT_{joint}]', 'STEPSPACE', f'c{card}_StepSpace_{tab}'],
				[f'[JOINT_{joint}]', 'DIRSETUP', f'c{card}_DirSetup_{tab}'],
				[f'[JOINT_{joint}]', 'DIRHOLD',  f'c{card}_DirHold_{tab}'],
				[f'[JOINT_{joint}]', 'MIN_LIMIT', f'c{card}_min_limit_{tab}'],
				[f'[JOINT_{joint}]', 'MAX_LIMIT',  f'c{card}_max_limit_{tab}'],
				[f'[JOINT_{joint}]', 'MAX_VELOCITY', f'c{card}_max_vel_{tab}'],
				[f'[JOINT_{joint}]', 'MAX_ACCELERATION', f'c{card}_max_accel_{tab}'],
				[f'[JOINT_{joint}]', 'SCALE', f'c{card}_scale_{tab}'],
				[f'[JOINT_{joint}]', 'HOME', f'c{card}_home_{tab}'],
				[f'[JOINT_{joint}]', 'HOME_OFFSET', f'c{card}_homeOffset_{tab}'],
				[f'[JOINT_{joint}]', 'HOME_SEARCH_VEL', f'c{card}_homeSearchVel_{tab}'],
				[f'[JOINT_{joint}]', 'HOME_LATCH_VEL', f'c{card}_homeLatchVel_{tab}'],
				[f'[JOINT_{joint}]', 'HOME_FINAL_VEL', f'c{card}_homeFinalVelocity_{tab}'],
				[f'[JOINT_{joint}]', 'HOME_USE_INDEX', f'c{card}_homeUseIndex_{tab}'],
				[f'[JOINT_{joint}]', 'HOME_IGNORE_LIMITS', f'c{card}_homeIgnoreLimits_{tab}'],
				[f'[JOINT_{joint}]', 'HOME_IS_SHARED', f'c{card}_homeSwitchShared_{tab}'],
				[f'[JOINT_{joint}]', 'HOME_SEQUENCE', f'c{card}_homeSequence_{tab}'],
				[f'[JOINT_{joint}]', 'P', f'c{card}_p_{tab}'],
				[f'[JOINT_{joint}]', 'I', f'c{card}_i_{tab}'],
				[f'[JOINT_{joint}]', 'D', f'c{card}_d_{tab}'],
				[f'[JOINT_{joint}]', 'FF0', f'c{card}_ff0_{tab}'],
				[f'[JOINT_{joint}]', 'FF1', f'c{card}_ff1_{tab}'],
				[f'[JOINT_{joint}]', 'FF2', f'c{card}_ff2_{tab}'],
				[f'[JOINT_{joint}]', 'DEADBAND', f'c{card}_deadband_{tab}'],
				[f'[JOINT_{joint}]', 'BIAS', f'c{card}_bias_{tab}'],
				[f'[JOINT_{joint}]', 'MAX_OUTPUT', f'c{card}_maxOutput_{tab}'],
				[f'[JOINT_{joint}]', 'MAX_ERROR', f'c{card}_maxError_{tab}'],
				[f'[JOINT_{joint}]', 'FERROR', f'c{card}_max_ferror_{tab}'],
				[f'[JOINT_{joint}]', 'MIN_FERROR', f'c{card}_min_ferror_{tab}'],
				[f'[JOINT_{joint}]', 'ENCODER_SCALE', f'c{card}_encoderScale_{tab}'],
				[f'[JOINT_{joint}]', 'ANALOG_SCALE_MAX', f'c{card}_analogScaleMax_{tab}'],
				[f'[JOINT_{joint}]', 'ANALOG_MIN_LIMIT', f'c{card}_analogMinLimit_{tab}'],
				[f'[JOINT_{joint}]', 'ANALOG_MAX_LIMIT', f'c{card}_analogMaxLimit_{tab}'],
				]

				for item in joint_list:
					self.update(parent, item[0], item[1], item[2])

		if '[SPINDLE_0]' in self.sections:
			parent.spindle_enable_cb.setChecked(True)
			parent.spindle_enable_cb.setEnabled(True)
			spindle = [
			['[SPINDLE_0]', 'SCALE', 'spindleEncoderScale'],
			['[SPINDLE_0]', 'SCALE', 'spindleStepScale'],
			['[SPINDLE_0]', 'PWM_FREQUENCY', 'pwmFrequencySB'],
			['[SPINDLE_0]', 'MIN_FORWARD_VELOCITY', 'spindle_fwd_min_rpm'],
			['[SPINDLE_0]', 'MAX_FORWARD_VELOCITY', 'spindle_fwd_max_rpm'],
			['[SPINDLE_0]', 'MIN_REVERSE_VELOCITY', 'spindle_rev_min_rpm'],
			['[SPINDLE_0]', 'MAX_REVERSE_VELOCITY', 'spindle_rev_max_rpm'],
			['[SPINDLE_0]', 'DEADBAND', 'deadband_s'],
			['[SPINDLE_0]', 'FEEDBACK', 'spindleFeedbackCB'],
			['[SPINDLE_0]', 'P', 'p_s'],
			['[SPINDLE_0]', 'I', 'i_s'],
			['[SPINDLE_0]', 'D', 'd_s'],
			['[SPINDLE_0]', 'FF0', 'ff0_s'],
			['[SPINDLE_0]', 'FF1', 'ff1_s'],
			['[SPINDLE_0]', 'FF2', 'ff2_s'],
			['[SPINDLE_0]', 'BIAS', 'bias_s'],
			['[SPINDLE_0]', 'MAX_ERROR', 'maxError_s'],
			['[SPINDLE_0]', 'DRIVE', 'spindleDriveCB'],
			['[SPINDLE_0]', 'STEPLEN', 'spindleStepTime'],
			['[SPINDLE_0]', 'STEPSPACE', 'spindleStepSpace'],
			['[SPINDLE_0]', 'DIRSETUP', 'spindleDirSetup'],
			['[SPINDLE_0]', 'DIRHOLD', 'spindleDirHold'],
			['[SPINDLE_0]', 'STEP_INVERT', 'spindleStepInvert'],
			['[SPINDLE_0]', 'DIR_INVERT', 'spindleDirInvert'],
			['[SPINDLE_0]', 'MAX_ACCEL_RPM', 'spindleMaxAccel'],
			['[SPINDLE_0]', 'CONNECTOR', 'connector_7i76_cb'],
			]

			board_name = parent.boardCB.currentText()
			# self.update_key(f'SPINDLE_0', 'CONNECTOR', parent.connector_7i76_cb.currentText())

			if board_name == '7i76E':
				spindle.append(['[SPINDLE_0]', 'MAX_OUTPUT', 'max_rpm_7i76e_sb'])
				spindle.append(['[SPINDLE_0]', 'SCALE_MAX', 'max_scale_7i76e_sb'])
			elif board_name == '7i76EU':
				spindle.append(['[SPINDLE_0]', 'MAX_OUTPUT', 'max_rpm_7i76eu_sb'])
				spindle.append(['[SPINDLE_0]', 'SCALE_MAX', 'max_scale_7i76eu_sb'])
			elif board_name == '7i96S':
				spindle.append(['[SPINDLE_0]', 'MAX_OUTPUT', 'max_rpm_7i96s_sb'])

			for item in spindle:
				self.update(parent, item[0], item[1], item[2])

		# 7i77 spindle on drive 5
		if '[SPINDLE_7I77]' in self.sections:
			start = self.sections['[SPINDLE_7I77]'][0]
			end = self.sections['[SPINDLE_7I77]'][1]
			for item in self.content[start:end]:
				if item.strip().startswith('CARD') and '=' in item:
					card = item.split('=')[1].strip()
					getattr(parent, f'c{card}_spindle_cb').setChecked(True)

					spindle_7i77 = [
					['[SPINDLE_7I77]', 'P', f'c{card}_p_5'],
					['[SPINDLE_7I77]', 'I', f'c{card}_i_5'],
					['[SPINDLE_7I77]', 'D', f'c{card}_d_5'],
					['[SPINDLE_7I77]', 'FF0', f'c{card}_ff0_5'],
					['[SPINDLE_7I77]', 'FF1', f'c{card}_ff1_5'],
					['[SPINDLE_7I77]', 'FF2', f'c{card}_ff2_5'],
					['[SPINDLE_7I77]', 'BIAS', f'c{card}_bias_5'],
					['[SPINDLE_7I77]', 'DEADBAND', f'c{card}_deadband_5'],
					['[SPINDLE_7I77]', 'MIN_RPM', f'c{card}_analogMinLimit_5'],
					['[SPINDLE_7I77]', 'MAX_RPM', f'c{card}_analogMaxLimit_5'],
					['[SPINDLE_7I77]', 'SCALE_MAX', f'c{card}_analogScaleMax_5'],
					]

					for item in spindle_7i77:
						self.update(parent, item[0], item[1], item[2])

		for i in range(4):
			for j in range(32):
				inputs = [
				['[INPUTS]', f'INPUT_{i}_{j}', f'c{i}_input_{j}'],
				['[INPUTS]', f'INPUT_INVERT_{i}_{j}', f'c{i}_input_invert_{j}'],
				['[INPUTS]', f'INPUT_SLOW_{i}_{j}', f'c{i}_input_debounce_{j}'],
				]

				for item in inputs:
					self.update(parent, item[0], item[1], item[2])

		for i in range(4):
			for j in range(16):
				outputs = [
				['[OUTPUTS]', f'OUTPUT_{i}_{j}', f'c{i}_output_{j}'],
				['[OUTPUTS]', f'OUTPUT_INVERT_{i}_{j}', f'c{i}_output_invert_{j}'],
				]

				for item in outputs:
					self.update(parent, item[0], item[1], item[2])

		# update output type if in configuration
		if '[OUTPUTS]' in self.sections:
			start = self.sections['[OUTPUTS]'][0]
			end = self.sections['[OUTPUTS]'][1]
			sink = ''
			source = ''
			for item in self.content[start:end]:
				if item.strip().startswith('OUTPUT_SINK') and '=' in item:
					sink = item.split('=')[1].strip()
				if item.strip().startswith('OUTPUT_SOURCE') and '=' in item:
					source = item.split('=')[1].strip()
			if len(sink) == 16 and len(source) == 16:
				for i in range(16):
					if sink[i] == '1' and source[i] == '0': # sink
						getattr(parent, f'c0_output_type_{i}').setCurrentIndex(1)
					elif sink[i] == '1' and source[i] == '1': # push pull
						getattr(parent, f'c0_output_type_{i}').setCurrentIndex(2)

		# check for custom, postgui and shutdown hal files
		

		options = [
		['[OPTIONS]', 'LOAD_CONFIG', 'load_config_cb'],
		['[OPTIONS]', 'INTRO_GRAPHIC', 'introGraphicLE'],
		['[OPTIONS]', 'INTRO_GRAPHIC_TIME', 'splashScreenSB'],
		['[OPTIONS]', 'MANUAL_TOOL_CHANGE', 'manualToolChangeCB'],
		['[OPTIONS]', 'CUSTOM_HAL', 'customhalCB'],
		['[OPTIONS]', 'POST_GUI_HAL', 'postguiCB'],
		['[OPTIONS]', 'SHUTDOWN_HAL', 'shutdownCB'],
		['[OPTIONS]', 'HALUI', 'haluiCB'],
		['[OPTIONS]', 'PYVCP', 'pyvcpCB'],
		['[OPTIONS]', 'GLADEVCP', 'gladevcpCB'],
		['[OPTIONS]', 'LADDER', 'ladderGB'],
		['[OPTIONS]', 'BACKUP', 'backupCB'],
		]

		for item in options:
			self.update(parent, item[0], item[1], item[2])

		plc = [
		['[PLC]','LADDER_RUNGS', 'ladderRungsSB'],
		['[PLC]','LADDER_BITS', 'ladderBitsSB'],
		['[PLC]','LADDER_WORDS', 'ladderWordsSB'],
		['[PLC]','LADDER_TIMERS', 'ladderTimersSB'],
		['[PLC]','LADDER_IEC_TIMERS', 'iecTimerSB'],
		['[PLC]','LADDER_MONOSTABLES', 'ladderMonostablesSB'],
		['[PLC]','LADDER_COUNTERS', 'ladderCountersSB'],
		['[PLC]','LADDER_HAL_INPUTS', 'ladderInputsSB'],
		['[PLC]','LADDER_HAL_OUTPUTS', 'ladderOutputsSB'],
		['[PLC]','LADDER_EXPRESSIONS', 'ladderExpresionsSB'],
		['[PLC]','LADDER_SECTIONS', 'ladderSectionsSB'],
		['[PLC]','LADDER_SYMBOLS', 'ladderSymbolsSB'],
		['[PLC]','LADDER_S32_INPUTS', 'ladderS32InputsSB'],
		['[PLC]','LADDER_S32_OUTPUTS', 'ladderS32OuputsSB'],
		['[PLC]','LADDER_FLOAT_INPUTS', 'ladderFloatInputsSB'],
		['[PLC]','LADDER_FLOAT_OUTPUTS', 'ladderFloatOutputsSB'],
		]

		for item in plc:
			self.update(parent, item[0], item[1], item[2])

		if '[SSERIAL]' in self.sections:
			start = self.sections['[SSERIAL]'][0]
			end = self.sections['[SSERIAL]'][1]
			for i, j in enumerate(range(start, end)):
				item = self.content[j].strip()
				if len(item) > 0 and '=' in item:
					line = item.split('=')
					key = line[0].strip()
					value = line[1].strip()
					if key == 'SS_CARD':
						self.update(parent, '[SSERIAL]', key, 'ssCardCB')
					elif key.startswith('ss'):
						if value != 'Select':
							self.update(parent, '[SSERIAL]', key, key)

		''' FIXME use settings
		# update the mesact.conf file
		configPath = os.path.expanduser('~/.config/measct/mesact.conf')
		config = ConfigParser()
		config.optionxform = str
		config.read(configPath)
		if config.has_option('NAGS', 'NEWUSER'):
			if parent.newUserCB.isChecked():
				config['NAGS']['NEWUSER'] = 'True'
		if config.has_option('STARTUP', 'CONFIG'):
			if parent.loadConfigCB.isChecked():
				config['STARTUP']['CONFIG'] = parent.configNameLE.text().lower()
		with open(configPath, 'w') as cf:
			config.write(cf)
		'''

		parent.loading = False

		if self.iniUnknown: # delete the ini file
			os.remove(self.iniFile)

		parent.status_lb.setText('Opened')
		parent.actionBuild.setText('Build Config')
		hal.open_hal(parent, os.path.split(iniFile)[0])

	def update(self, parent, section, key, obj):
		booleanDict = {'true': True, 'yes': True, '1': True,
			'false': False, 'no': False, '0': False,}
		if section in self.sections:
			start = self.sections[section][0]
			end = self.sections[section][1]
			for item in self.content[start:end]:
				if '=' in item:
					if item.split('=')[0].strip() == key:
						value = item.split('=')[1].strip()
						if isinstance(getattr(parent, obj), QComboBox):
							index = 0
							if getattr(parent, obj).findData(value) >= 0:
								index = getattr(parent, obj).findData(value)
							elif getattr(parent, obj).findText(value) >= 0:
								index = getattr(parent, obj).findText(value)
							if index >= 0:
								getattr(parent, obj).setCurrentIndex(index)
						elif isinstance(getattr(parent, obj), QLabel):
							getattr(parent, obj).setText(value)
						elif isinstance(getattr(parent, obj), QLineEdit):
							getattr(parent, obj).setText(value)
						elif isinstance(getattr(parent, obj), QSpinBox):
							getattr(parent, obj).setValue(abs(int(value.split('.')[0])))
						elif isinstance(getattr(parent, obj), QDoubleSpinBox):
							getattr(parent, obj).setValue(float(value))
						elif isinstance(getattr(parent, obj), QCheckBox):
							getattr(parent, obj).setChecked(booleanDict[value.lower()])
						elif isinstance(getattr(parent, obj), QRadioButton):
							getattr(parent, obj).setChecked(booleanDict[value.lower()])
						elif isinstance(getattr(parent, obj), QGroupBox):
							getattr(parent, obj).setChecked(booleanDict[value.lower()])
						elif isinstance(getattr(parent, obj), QPushButton):
							getattr(parent, obj).setText(value)

	def get_sections(self):
		self.sections = {}
		end = len(self.content)
		for index, line in enumerate(self.content):
			if line.strip().startswith('['):
				self.sections[line.strip()] = [index + 1, end]

		# set start and stop index for each section
		previous = ''
		for key, value in self.sections.items():
			if previous:
				self.sections[previous][1] = value[0] - 2
			previous = key

	def loadReadMe(self, parent, configName):
		configsDir = os.path.expanduser('~/linuxcnc/configs')
		readmeFile = os.path.join(configsDir, configName, 'README')
		if os.path.isfile(readmeFile):
			with open(readmeFile) as f:
				contents = f.read()
			parent.readme_pte.appendPlainText(contents)

