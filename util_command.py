class CommandManager:
    def __init__(self):
        # 相机基础功能指令
        self._camera_basic_commands = {
            'camera_mode': 'sfcmd cammode',            # 相机模式设置
            'image_size': 'sfcmd imgsize',             # 图片分辨率设置
            'video_size': 'sfcmd videosize',           # 视频分辨率设置
            'video_length': 'sfcmd videolen',          # 视频录制时长
            'flash_led': 'sfcmd flashled',             # 闪光灯控制
            'image_level': 'sfcmd imagelevel',         # 图片压缩等级
            'night_mode': 'sfcmd nightmode',           # 夜间模式设置
            'zoom': 'sfcmd zoom',                      # 变焦比例设置
            'night_vision': 'sfcmd nightvision',       # 夜视功能设置
        }

        # 拍摄功能指令
        self._camera_shoot_commands = {
            'multishot': 'sfcmd multishot',            # 连拍张数
            'multishot_interval': 'sfcmd multishotinterval',  # 连拍间隔
            'pir_switch': 'sfcmd pirsw',              # PIR功能开关
            'pir_sensitivity': 'sfcmd pirsen',         # PIR灵敏度
            'pir_delay': 'sfcmd pirdelay',            # PIR延迟设置
            'timelapse': 'sfcmd timelapse',           # 延时摄影设置
            'slow_motion': 'sfcmd slowmotion',        # 慢动作比例设置
        }

        # 系统设置指令
        self._system_commands = {
            'work_time': 'sfcmd worktime',            # 工作时间设置
            'date_style': 'sfcmd datestyle',          # 日期格式设置
            'battery_type': 'sfcmd battype',          # 电池类型设置
            'sd_loop': 'sfcmd sdloop',                # SD卡循环存储
            'stamp_switch': 'sfcmd stampsw',          # 水印功能开关
            'rtc_set': 'sfcmd rtcset',                # RTC时间设置
            'audio_volume': 'sfcmd audiovolume',      # 音量设置
            'status_light': 'sfcmd statuslight',      # 状态指示灯设置
            'camera_name': 'sfcmd camname',           # 相机名称设置
            'auto_off_switch': 'sfcmd autooffsw',     # 自动关机开关
            'auto_off_time': 'sfcmd autoofftime',     # 自动关机时间
        }

        # 网络相关指令
        self._network_commands = {
            'ftp_switch': 'sfcmd ftpswitch',          # FTP开关设置
            'video_options': 'sfcmd videooptions',     # 视频发送选项
            'ftp_server': 'sfcmd ftp',                # FTP服务器设置
            'send_mode': 'sfcmd sendmode',            # 发送模式设置
            'gprs_switch': 'sfcmd gprssw',            # GPRS开关
            'gprs_mode': 'sfcmd gprsmode',            # GPRS模式设置
            'send_max': 'sfcmd sendmax',              # 每日最大发送数
            'send_pic_size': 'sfcmd sendpicsize',     # 发送图片尺寸
            'start_time': 'sfcmd starttime',          # 批量发送开始时间
            '4g_write': 'sfcmd 4gttyw',              # 4G AT命令设置
            '4g_read': 'sfcmd 4gttyr',               # 4G AT命令读取
            'gps_switch': 'sfcmd gpssw',              # GPS开关
            'sim_pin_set': 'sfcmd simpinset',         # SIM卡PIN设置
        }

        # 调试和维护指令
        self._debug_commands = {
            'mcu_write': 'sfcmd mcuw',               # MCU寄存器写入
            'mcu_write_end': 'sfcmd mcuwe',          # MCU寄存器写入(带结束)
            'mcu_read': 'sfcmd mcur',                # MCU寄存器读取
            'p2p_did_get': 'sfcmd p2pdidget',        # 获取P2P DID
            'debug_mode_set': 'sfcmd endebugmodeset', # 调试模式设置
            'debug_mode': 'sfcmd debugmode',          # 调试模式
            'qlog_switch': 'sfcmd qlogsw',           # Qlog开关
            'log_level': 'sfcmd loglevel',           # 日志等级设置
            'dsp_upgrade': 'sfcmd dspupgrade',       # DSP固件升级
            'module_upgrade': 'sfcmd moduleupgrade',  # 模块升级
            'module_version': 'sfcmd moduleverset',   # 模块版本
        }

        # 系统工具指令
        self._utility_commands = {
            'print': 'sfcmd print',                   # 显示UI参数值
            'save': 'sfcmd save',                     # 保存UI参数到闪存
            'help': 'sfcmd help',                     # 打印帮助信息
        }

        # 动态指令集
        self._dynamic_commands = {}

    # ... 其他方法保持不变 ...
        # 动态指令集
        self._dynamic_commands = {}
        
    def add_command(self, key, command, category='dynamic'):
        """添加新指令"""
        if category == 'camera':
            self._camera_commands[key] = command
        elif category == 'system':
            self._system_commands[key] = command
        else:
            self._dynamic_commands[key] = command
            
    def remove_command(self, key):
        """移除指令"""
        for cmd_dict in [self._camera_commands, self._system_commands, self._dynamic_commands]:
            if key in cmd_dict:
                del cmd_dict[key]
                return True
        return False
        
    def get_command(self, key):
        """获取指令"""
        for cmd_dict in [self._camera_commands, self._system_commands, self._dynamic_commands]:
            if key in cmd_dict:
                return cmd_dict[key]
        return None
        
    def update_from_server(self, new_commands):
        """从服务器更新指令"""
        for key, value in new_commands.items():
            self.add_command(key, value)
            
    @property
    def all_commands(self):
        """获取所有指令"""
        all_cmds = {}
        all_cmds.update(self._camera_commands)
        all_cmds.update(self._system_commands)
        all_cmds.update(self._dynamic_commands)
        return all_cmds