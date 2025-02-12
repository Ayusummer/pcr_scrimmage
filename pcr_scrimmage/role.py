##可用角色

"""
##可用角色可自定义增加，详细看下面的示例

基础属性：
	name			名字		string
	health			生命值		number
	distance		攻击距离	number
	attack			攻击力		number
	defensive		防御力		number
	tp				能量值		number
	crit			暴击		float	暴击概率百分比，1为100%
	active_skills	主动技能	list[dict]
	passive_skills	被动技能	list[dict] 依赖主动技能
		被动技能的主要作用，是为了让一个主动技能可以同时选择不同的触发对象
		例如：yly，砍别人一刀自己掉血
		被动技能优先级比主动高，可以先对自身增加攻击力后再进行攻击
		（其实，把这个 “被动技能” 说成是 “附带效果” 也可以，单纯为了区分不同的触发对象而已）

技能：
	name			技能名称	string
	text			技能描述	string
	tp_cost			消耗tp		number
	effect			技能效果	list[dict]
	trigger			触发对象	string
	passive			被动		list[number] 数字对应基础属性的passive_skill

	################（技能效果可增加，增加后在 skillEffect() 里做处理）################
	效果effect：(可选单个或多个) (被动技能：对自己和对目标的效果要分开)
		attr				属性改变，如果要同时改变多个属性值，每个属性都需要单独添加一条被动

		move				移动，正数为前进负数为后退	number
		move_goal			向目标移动（一个技能有多个效果且包括向目标移动，向目标移动效果必须最先触发）
							这个效果必须放在被动
		ignore_dist			无视距离，参数填啥都行，不会用到

		make_it_out_tp		令目标出局时tp变动
		make_it_out_turn	令目标出局时锁定回合

	################触发对象可继续增加，添加后在 skillTrigger() 里做处理################
	触发对象trigger：
		select				选择目标

		all					对所有人有效(包括自己)
		all_except_me		对所有人有效(除了自己)
		me					只对自己有效

		near				离自己最近

"""



EFFECT_HURT = "hurt"					#造成伤害	tuple元组 (数值，加成类型，加成的数值对象，加成比例，是否为真实伤害)
										#加成类型：attr.py , 为0时无加成; 加成的数值对象：0自己 1目标
EFFECT_ELIMINATE = "eliminate"			#斩杀效果，目标生命值越低造成的伤害越高		tuple元组 (目标生命值降低比例, 伤害数值)
										#EFFECT_ELIMINATE需要EFFECT_HURT作为前置
EFFECT_LIFESTEAL = "life_steal"			#生命偷取	float 伤害-生命值之间的转换比例
										#EFFECT_LIFESTEAL需要EFFECT_HURT作为前置

EFFECT_BUFF = "buff"					#buff效果		list[tuple,tuple] [(BuffType.xx, 数值, 可触发次数), (...)]
EFFECT_BUFF_BY_BT = "buff_by_bt"		#buff效果触发(通过buff类型)	list[BuffType]		立即触发指定buff类型的buff效果
										#EFFECT_BUFF_BY_BT需要EFFECT_BUFF作为前置
EFFECT_ATTR_CHANGE = "attr"				#属性改变，正数为增加，负数为减少	list[tuple,tuple] [(属性类型，数值，加成类型，加成比例), (...)]
										#属性类型/加成类型：attr.py , 为0时无加成

EFFECT_MOVE = "move"					#移动，正数为前进负数为后退（触发跑道事件）	number
EFFECT_MOVE_GOAL = "move_goal"			#向目标移动（一个技能有多个效果且包括向目标移动，向目标移动效果必须最先触发） tuple元组(移动距离，是否无视攻击范围)
										#这个效果必须放在被动（不触发跑道事件）
EFFECT_IGNORE_DIST = "ignore_dist"		#无视距离效果，参数随便填，不会用到
										#这个效果必须放在被动
EFFECT_AOE = "aoe"						#范围效果			tuple	(半径范围, 是否对自己生效)
EFFECT_HIT_BACK = "hit_back"			#击退				number	填正数为击退x格子，负数为拉近
EFFECT_LOCKTURN = "lock_turn"			#锁定回合			number	不会切换到下一个玩家，当前玩家继续丢色子和放技能
EFFECT_SKILL_CHANGE = "skill_change"	#更改技能			tuple	(BuffType.xx, [被动技能编号1, 被动技能编号2])
										#当自身存在某个特定buff时，技能效果替换为特定被动效果，原效果不触发

EFFECT_OUT_TP = "make_it_out_tp"		#令目标出局时tp变动		number
EFFECT_OUT_LOCKTURN = "make_it_out_turn"#令目标出局时锁定回合	number	锁定回合：不会切换到下一个玩家，当前玩家继续丢色子和放技能


TRIGGER_SELECT = "select"						#选择目标(包括自己)
TRIGGER_SELECT_EXCEPT_ME = "select_except_me"	#选择目标(除了自己)
TRIGGER_ALL = "all"								#对所有人有效(包括自己)
TRIGGER_ALL_EXCEPT_ME = "all_except_me"			#对所有人有效(除了自己)
TRIGGER_ME = "me"								#只对自己有效
TRIGGER_NEAR = "near"							#离自己最近的目标

from .attr import Attr
from .buff import BuffType, BuffTriggerType

# 角色字典
ROLE = {
	#注意：id要和_pcr_data.py里对应角色一样
	1068:{
		"name":"晶(beta α)",

		"health":1250,
		"distance":9,
		"attack":70,
		"defensive":100,
		"crit":15,
		"tp":0,

		"active_skills" : [
			{
				"name":"普通攻击",
				"text":"对目标造成0(+1.0自身攻击力)伤害,并回复10点TP",
				"tp_cost":0,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[2],

				"effect":{
					EFFECT_HURT:(0, Attr.ATTACK, 0, 1, False)
				}
			},
			{
				"name":"热身!",
				"text":"热身！:增加自己80攻击力、15%的暴击率持续4回合,并减少周围角色10点永久攻击力。\n",
				"tp_cost":20,
				"trigger": TRIGGER_ME,
				"passive":[0],
				"effect":{
					EFFECT_BUFF:[
						(BuffType.NormalAttrAtkUp, 80, 4),
						(BuffType.NormalAttrCritUp, 15, 4)
					],
				}
			},
			{
				"name":"岩石穿刺",
				"text":"岩石穿刺！:降低目标玩家100点防御力，持续4个玩家回合，并造成80(+1.5自身攻击力),造成伤害的15%转为生命值。 \n",
				"tp_cost":30,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[],
				"effect":{
					EFFECT_BUFF:[(BuffType.NormalAttrDefDown, -100, 4)],
					EFFECT_HURT:(80, Attr.ATTACK, 0, 1.5, False),
					EFFECT_LIFESTEAL:0.15,
				}
			},
			{
				"name":"万物改造",
				"text":"使用七冠权力，大幅提升自身属性，并降低其他玩家防御力，回复30TP后继续1回合。",
				"tp_cost":100,
				"trigger": TRIGGER_ME,
				"passive":[1],
				"effect":{
					EFFECT_ATTR_CHANGE:[(Attr.NOW_TP, 30, 0, 0)],
					EFFECT_BUFF:[
						(BuffType.NormalAttrAtkUp, 200, 99999),
						(BuffType.NormalAttrCritUp, 25, 99999),
						(BuffType.NormalAttrDefUp, 30, 99999)
					],
					EFFECT_LOCKTURN:1
				}
			}
		],
		"passive_skills": [
			{
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"effect":{
					EFFECT_ATTR_CHANGE:[(Attr.ATTACK, -10, 0, 0)],
					EFFECT_AOE:(3, False),
				}
			},
			{
				"trigger": TRIGGER_ALL_EXCEPT_ME,
				"effect":{
					EFFECT_BUFF:[(BuffType.NormalAttrDefDown, 1000, 99999)],
				}
			},
			{
				"trigger": TRIGGER_ME,
				"effect":{
					EFFECT_ATTR_CHANGE:[(Attr.NOW_TP, 10, 0, 0)],
				}
			}
		]
	},
	1061:{
		"name":"矛依未",

		"health":1300,
		"distance":5,
		"attack":130,
		"defensive":60,
		"crit":10,
		"tp":0,

		"active_skills" : [
			{
				"name":"普通攻击",
				"text":"对目标造成0(+1.0自身攻击力)伤害,并回复3点TP",
				"tp_cost":0,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[4],

				"effect":{
					EFFECT_HURT:(0, Attr.ATTACK, 0, 1, False)
				}
			},
			{
				"name":"吓到你发抖！/ 天楼回刃斩",
				"text":("吓到你发抖！:对目标造成50(+0.8自身攻击力)伤害，并降低30点攻击力持续3玩家回合，且将其击退5步 \n" + 
						"\t天楼回刃斩：对目标造成125(+1.25自身攻击力)伤害，并将造成伤害的12%转化为生命值"),
				"tp_cost":30,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[],
				"effect":{
					EFFECT_HURT:(50, Attr.ATTACK, 0, 0.8, False),
					EFFECT_BUFF:[(BuffType.NormalAttrAtkDown, -30, 3)],
					EFFECT_HIT_BACK:5,
					EFFECT_SKILL_CHANGE:(BuffType.TenRouHaDanKen, [0]),
				}
			},
			{
				"name":"这边啦这边！/ 天楼闪薙斩",
				"text":("这边啦这边！:降低目标及其半径范围2以内所有玩家45点防御力，持续8个玩家回合，并减少30TP \n" + 
						"\t天楼闪薙斩：对目标及其半径范围3以内所有玩家造成100(+0.6自身攻击力)伤害，并将造成伤害的5%转化为生命值"),
				"tp_cost":20,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[],
				"effect":{
					EFFECT_ATTR_CHANGE:[(Attr.NOW_TP, -30, 0, 0)],
					EFFECT_BUFF:[(BuffType.NormalAttrDefDown, -45, 8)],
					EFFECT_AOE:(2, False),
					EFFECT_SKILL_CHANGE:(BuffType.TenRouHaDanKen, [1]),
				}
			},
			{
				"name":"天楼霸断剑",
				"text":"对目标造成50(+0.8自身攻击力)伤害，并巨幅增加自身所有属性，持续全场！",
				"tp_cost":100,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[2],
				"effect":{
					EFFECT_HURT:(50, Attr.ATTACK, 0, 0.8, False),
				}
			}
		],
		"passive_skills": [
			{
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"effect":{
					EFFECT_HURT:(125, Attr.ATTACK, 0, 1.25, False),
					EFFECT_LIFESTEAL:0.12,
				}
			},
			{
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"effect":{
					EFFECT_HURT:(100, Attr.ATTACK, 0, 0.6, False),
					EFFECT_AOE:(3, False),
					EFFECT_LIFESTEAL:0.05,
				}
			},
			{
				"trigger": TRIGGER_ME,
				"effect":{
					EFFECT_BUFF:[(BuffType.TenRouHaDanKen, 0, 99999),
								(BuffType.NormalAttrAtkUp, 120, 99999),
								(BuffType.NormalAttrCritUp, 20, 99999),
								(BuffType.NormalAttrMaxHelUp, 250, 99999)],
					EFFECT_ATTR_CHANGE:[(Attr.NOW_TP, 100, 0, 0)],
					EFFECT_BUFF_BY_BT:[ BuffType.NormalAttrAtkUp,
										BuffType.NormalAttrCritUp,
										BuffType.NormalAttrMaxHelUp],
				}
			},
			{
				"trigger": TRIGGER_ME,
				"effect":{
					EFFECT_ATTR_CHANGE:[(Attr.NOW_TP, 3, 0, 0)],
				}
			}
		]
	},
	1060:{
		"name":"凯露",

		"health":1050,
		"distance":10,
		"attack":125,
		"defensive":60,
		"crit":20,
		"tp":0,

		"active_skills" : [
			{
				"name":"普通攻击",
				"text":"对目标造成0(+1.0自身攻击力)伤害",
				"tp_cost":10,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[],

				"effect":{
					EFFECT_HURT:(0, Attr.ATTACK, 0, 1, False)
				}
			},
			{
				"name":"闪电球",
				"text":"对目标及其范围1内的敌人造成70(+0.7自身攻击力)伤害并减少50防御(持续4回合)，并增加自身20点攻击力",
				"tp_cost":20,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[0],
				"effect":{
					EFFECT_HURT:(70, Attr.ATTACK, 0, 0.7, False),
					EFFECT_BUFF:[(BuffType.NormalAttrDefDown, -50, 4)],
					EFFECT_AOE:(1, False),
				}
			},
			{
				"name":"能量吸附",
				"text":"对目标造成50(+1.5自身攻击力)伤害，并将造成伤害的30%转换为自身生命值，并回复自身20点TP",
				"tp_cost":30,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[1],
				"effect":{
					EFFECT_HURT:(50, Attr.ATTACK, 0, 1.5, False),
					EFFECT_LIFESTEAL:0.3,
				}
			},
			{
				"name":"格林爆裂",
				"text":"对所有人造成100(+2.25自身攻击力)真实伤害",
				"tp_cost":60,
				"trigger": TRIGGER_ALL_EXCEPT_ME,
				"passive":[],
				"effect":{
					EFFECT_HURT:(100, Attr.ATTACK, 0, 2.25, True),
				}
			}
		],
		"passive_skills": [
			{
				"trigger": TRIGGER_ME,
				"effect":{
					EFFECT_ATTR_CHANGE:[(Attr.ATTACK, 20, 0, 0)],
				}
			},
			{
				"trigger": TRIGGER_ME,
				"effect":{
					EFFECT_ATTR_CHANGE:[(Attr.NOW_TP, 20, 0, 0)],
				}
			}
		], 
				
     },
	
	1059:{
		"name":"可可萝",

		"health":1000,
		"distance":6,
		"attack":50,
		"defensive":70,
		"crit":5,
		"tp":0,

		"active_skills" : [
			{
				"name":"普通攻击",
				"text":"对目标造成0(+1.0自身攻击力)伤害",
				"tp_cost":0,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[],

				"effect":{
					EFFECT_HURT:(0, Attr.ATTACK, 0, 1, False)
				}
			},
			{
				"name":"三连击",
				"text":"向目标移动3格，并对目标造成100(+1.5自身攻击力)伤害",
				"tp_cost":20,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[0],
				"effect":{
					EFFECT_HURT:(100, Attr.ATTACK, 0, 1.5, False)
				}
			},
			{
				"name":"极光守护",
				"text":"增加1000点防御力，持续4个玩家回合",
				"tp_cost":20,
				"trigger": TRIGGER_ME,
				"passive":[],
				"effect":{
					EFFECT_BUFF:[(BuffType.NormalAttrDefUp, 1000, 4)],
				}
			},
			{
				"name":"光之加护",
				"text":"自身回复300点生命值，并增加50点攻击力",
				"tp_cost":50,
				"trigger": TRIGGER_ME,
				"passive":[],
				"effect":{
					EFFECT_ATTR_CHANGE:[
						(Attr.NOW_HEALTH, 250, 0, 0),
						(Attr.ATTACK, 50, 0, 0)],
				}
			}
		],
		"passive_skills": [
			{
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"effect":{
					EFFECT_MOVE_GOAL:(3, False),
				}
			}
		]
	},
	1058:{
		"name":"佩可",

		"health":1800,
		"distance":5,
		"attack":55,
		"defensive":82,
		"crit":5,
		"tp":0,

		"active_skills" : [
			{
				"name":"普通攻击",
				"text":"对目标造成0(+1.8自身攻击力)伤害",
				"tp_cost":0,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[],

				"effect":{
					EFFECT_HURT:(0, Attr.ATTACK, 0, 1.8, False)
				}
			},
			{
				"name":"跳砍",
				"text":"对目标造成50(+0.5自身防御力)伤害",
				"tp_cost":20,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[],

				"effect":{
					EFFECT_HURT:(50, Attr.DEFENSIVE, 0, 0.5, False)
				}
			},
			{
				"name":"超大饭团",
				"text":"回复自身100(+0.8自身防御力)生命值，并增加22点防御力",
				"tp_cost":25,
				"trigger": TRIGGER_ME,
				"passive":[],

				"effect":{
					EFFECT_ATTR_CHANGE:[
						(Attr.NOW_HEALTH, 100, Attr.DEFENSIVE, 0.8),
						(Attr.DEFENSIVE, 22, 0, 0)],
				}
			},
			{
				"name":"公主突袭",
				"text":"向目标移动5格，对目标造成225真实伤害，并增加自身48点防御力",
				"tp_cost":45,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[0,1],

				"effect":{
					EFFECT_HURT:(225, Attr.ATTACK, 0, 0, True),
				}
			}
		],
		"passive_skills": [
			{
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"effect":{
					EFFECT_MOVE_GOAL:(5, False),
				}
			},
			{
				"trigger": TRIGGER_ME,
				"effect":{
					EFFECT_ATTR_CHANGE:[(Attr.DEFENSIVE, 48, 0, 0)],
				}
			}
		]
	},
	1052:{
		"name":"莉玛",
		"health":2000,
		"distance":5,
		"attack":0,
		"defensive":160,
		"crit":0,
		"tp":0,

		"active_skills":[
			{
				"name":"普通攻击",
				"text":"对目标造成30真实伤害",
				"tp_cost":0,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[],

				"effect":{
					EFFECT_HURT:(30, Attr.ATTACK, 0, 0, True)
				}
			},
			{
				"name":"护盾",
				"text":"为自己增加一个200点生命值的护盾（只可触发1次），并增加10点防御力",
				"tp_cost":30,
				"trigger": TRIGGER_ME,
				"passive":[],

				"effect":{
					EFFECT_BUFF:[(BuffType.Shield, 200, 1)],
					EFFECT_ATTR_CHANGE:[(Attr.DEFENSIVE, 10, 0, 0)],
				}
			},
			{
				"name":"毛茸茸突袭",
				"text":"向目标移动3格，对目标造成60(+0.3自身防御力)伤害，并增加自身32点防御",
				"tp_cost":24,
				"trigger":TRIGGER_SELECT_EXCEPT_ME,
				"passive":[0,1],
				
				"effect":{
					EFFECT_HURT:(60, Attr.DEFENSIVE, 0, 0.3, False),
				}
			},
			{
				"name":"毛茸茸挥击",
				"text":"向目标移动4格，对目标造成140(+0.8自身防御力)伤害，并增加自身75点防御",
				"tp_cost":66,
				"trigger":TRIGGER_SELECT_EXCEPT_ME,
				"passive":[2,3],

				"effect":{
					EFFECT_HURT:(140, Attr.DEFENSIVE, 0, 0.8, False),
				},
			}
		],
		"passive_skills":[
			{
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"effect":{
					EFFECT_MOVE_GOAL:(3, False),
				}
			},
			{
				"trigger": TRIGGER_ME,
				"effect":{
					EFFECT_ATTR_CHANGE:[(Attr.DEFENSIVE, 32, 0, 0)],
				}
			},
			{
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"effect":{
					EFFECT_MOVE_GOAL:(4, False),
				}
			},
			{
				"trigger": TRIGGER_ME,
				"effect":{
					EFFECT_ATTR_CHANGE:[(Attr.DEFENSIVE, 75, 0, 0)],
				}
			},
		]
	},
	1044:{
		"name":"伊莉亚",
		"health":1280,
		"distance":7,
		"attack":180,
		"defensive":40,
		"crit":25,
		"tp":0,

		"active_skills":[
			{
				"name":"普通攻击",
				"text":"对目标造成0(+0.8自身攻击力)真实伤害，并回复所造成伤害50%生命值",
				"tp_cost":0,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[],

				"effect":{
					EFFECT_HURT:(0, Attr.ATTACK, 0, 0.8, True),
					EFFECT_LIFESTEAL:0.5
				}
			},
			{
				"name":"血腥爆破",
				"text":"对目标造成120(+0.8自身攻击力)的真实伤害,并提升自身25攻击力、回复所造成伤害40%生命值,且对自身造成60(+0.6攻击力)伤害",
				"tp_cost":25,
				"trigger":TRIGGER_SELECT_EXCEPT_ME,
				"passive":[0,1],

				"effect":{
					EFFECT_HURT:(120, Attr.ATTACK, 0, 0.8, True),
					EFFECT_LIFESTEAL:0.4
				}
			},
			{
				"name":"血腥之矛",
				"text":"对目标及其半径4范围内的所有玩家造成140(+0.5自身攻击力)的真实伤害,并回复所造成伤害25%生命值,且对自身造成45(+0.8攻击力)伤害",
				"tp_cost":20,
				"trigger":TRIGGER_SELECT_EXCEPT_ME,
				"passive":[2],
				
				"effect":{
					EFFECT_AOE:(4, False),
					EFFECT_HURT:(140, Attr.ATTACK, 0, 0.5, True),
					EFFECT_LIFESTEAL:0.25
				}
			},
			{
				"name":"朱色之噬",
				"text":"对目标及其半径3范围内除自己外的所有玩家造成150(+1.2自身攻击力)的真实伤害,并回复所造成伤害60%生命值",
				"tp_cost":60,
				"trigger":TRIGGER_SELECT_EXCEPT_ME,
				"passive":[],

				"effect":{
					EFFECT_AOE:(3, False),
					EFFECT_HURT:(150, Attr.ATTACK, 0, 1.2, True),
					EFFECT_LIFESTEAL:0.6,
				}
			}
		],
		"passive_skills":[
			{
				"trigger":TRIGGER_ME,
				"effect":{
					EFFECT_ATTR_CHANGE:[(Attr.ATTACK, 25, 0, 0)],
				}
			},
			{
				"trigger":TRIGGER_ME,
				"effect":{
					EFFECT_HURT:(60, Attr.ATTACK, 0, 0.6, False),
				}
			},
			{
				"trigger":TRIGGER_ME,
				"effect":{
					EFFECT_HURT:(45, Attr.ATTACK, 0, 0.8, False),
				}
			}
		]
	},
	1038:{
		"name":"栞",
		"health":825,
		"distance":10,
		"attack":80,
		"defensive":60,
		"crit":5,
		"tp":0,

		"active_skills" : [
			{
				"name":"普通攻击",
				"text":"对目标造成0(+0.5自身攻击力)伤害",
				"tp_cost":0,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[],

				"effect":{
					EFFECT_HURT:(0, Attr.ATTACK, 0, 0.5, False)
				}
			},
			{
				"name":"风之箭",
				"text":"对目标造成80(+1.45自身攻击力)伤害,并自身回复50tp",
				"tp_cost":20,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[0],

				"effect":{
					EFFECT_HURT:(-80, Attr.ATTACK, 0, 1.45, False)
				}
			},
			{
				"name":"三重箭矢",
				"text":"对除自己外所有玩家造成70(+0.8自身攻击力)伤害,并自身回复50tp",
				"tp_cost":20,
				"trigger": TRIGGER_ALL_EXCEPT_ME,
				"passive":[0],

				"effect":{
					EFFECT_HURT:(70, Attr.ATTACK, 0, 0.8, False)
				}
			},
			{
				"name":"附魔之箭",
				"text":"对目标造成120(+1.5自身攻击力)伤害,并提升自身100攻击力和回复50tp",
				"tp_cost":100,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[0,1],

				"effect":{
					EFFECT_HURT:(120, Attr.ATTACK, 0, 1.5, False)
				}
			}
		],
		"passive_skills": [
				{
				"trigger": TRIGGER_ME,
				"effect":{
					EFFECT_ATTR_CHANGE:[(Attr.NOW_TP, 50, 0, 0)]
					}
				},
				{
				"trigger": TRIGGER_ME,
				"effect":{
					EFFECT_ATTR_CHANGE:[(Attr.ATTACK, 100, 0, 0)]
					}
				}
		]
	},
	1036:{
		"name":"镜华",
		"health":800,
		"distance":15,
		"attack":150,
		"defensive":50,
		"crit":0,
		"tp":0,

		"active_skills" : [
			{
				"name":"普通攻击",
				"text":"对目标造成0(+1.0自身攻击力)伤害",
				"tp_cost":10,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[],

				"effect":{
					EFFECT_HURT:(0, Attr.ATTACK, 0, 1, False)
				}
			},
			{
				"name":"魔法增幅",
				"text":"自身增加50点攻击力, 且下次攻击增加70%暴击概率",
				"tp_cost":20,
				"trigger": TRIGGER_ME,
				"passive":[],

				"effect":{
					EFFECT_ATTR_CHANGE:[(Attr.ATTACK, 50, 0, 0)],
					EFFECT_BUFF:[(BuffType.AttackAttrCritUp, 70, 1)],
				}
			},
			{
				"name":"冰枪术",
				"text":"对目标造成20(+1.5自身攻击力)伤害",
				"tp_cost":30,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[],

				"effect":{
					EFFECT_HURT:(20, Attr.ATTACK, 0, 1.5, False)
				}
			},
			{
				"name":"宇宙苍蓝闪",
				"text":"无视距离，对目标造成50(+2.2自身攻击力)伤害",
				"tp_cost":70,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[0],

				"effect":{
					EFFECT_HURT:(50, Attr.ATTACK, 0, 2.2, False),
				}
			}
		],
		"passive_skills": [
			{
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"effect":{
					EFFECT_IGNORE_DIST:0,
				}
			},
		]
	},
	1034:{
		"name":"优花梨",
		"health":1200,
		"distance":7,
		"attack":0,
		"defensive":120,
		"crit":0,
		"tp":20,

		"active_skills":[
			{
				"name":"肉蛋葱鸡",
				"text":"无视距离，向离自己最近的目标移动3步，并对目标造成0(+1.2自身防御力)伤害",
				"tp_cost":10,
				"trigger": TRIGGER_NEAR,
				"passive":[0],

				"effect":{
					EFFECT_HURT:(0, Attr.DEFENSIVE, 0, 1.2, False)
				}
			},
			{
				"name":"护盾",
				"text":"为自己增加一个350点生命值的护盾（只可触发1次），并增加25点防御力",
				"tp_cost":20,
				"trigger": TRIGGER_ME,
				"passive":[],

				"effect":{
					EFFECT_BUFF:[(BuffType.Shield, 350, 1)],
					EFFECT_ATTR_CHANGE:[(Attr.DEFENSIVE, 25, 0, 0)],
				}
			},
			{
				"name":"月下独酌",
				"text":"自身增加30TP, 并恢复自身防御力70%的生命值",
				"tp_cost":20,
				"trigger":TRIGGER_ME,
				"passive":[],
				
				"effect":{
					EFFECT_ATTR_CHANGE:[
						(Attr.NOW_HEALTH, 0, Attr.DEFENSIVE, 0.7),
						(Attr.NOW_TP, 50, 0, 0)],
				},
			},
			{
				"name":"第七天堂",
				"text":"提升全体40防御,回复全体根据自身防御90%生命值,自身额外提升60防御和200生命值",
				"tp_cost":80,
				"trigger":TRIGGER_ALL,
				"passive":[1],

				"effect":{
					EFFECT_ATTR_CHANGE:[
						(Attr.NOW_HEALTH, 0, Attr.DEFENSIVE, 0.9),
						(Attr.DEFENSIVE, 40, 0, 0)],
				},
			}
		],
		"passive_skills":[
			{
				"trigger": TRIGGER_NEAR,
				"effect":{
					EFFECT_MOVE_GOAL:(3, False),
				}
			},
			{
				"trigger": TRIGGER_ME,
				"effect":{
					EFFECT_ATTR_CHANGE:[
						(Attr.DEFENSIVE, 60, 0, 0),
						(Attr.NOW_HEALTH,200, 0, 0)],
				},
			}
		]
	},
	1022:{
		"name":"依里",
		"health":900,
		"distance":10,
		"attack":120,
		"defensive":50,
		"crit":5,
		"tp":0,


		"active_skills" : [
			{
				"name":"普通攻击",
				"text":"对目标造成0(+1.0自身攻击力)伤害",
				"tp_cost":10,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[],

				"effect":{
					EFFECT_HURT:(0, Attr.ATTACK, 0, 1, False)
				}
			},
			{
				"name":"极限充能",
				"text":"消耗自身150HP提高70攻击力，并自身回复30TP",
				"tp_cost":0,
				"trigger": TRIGGER_ME,
				"passive":[],

				"effect":{
					EFFECT_ATTR_CHANGE:[
						(Attr.ATTACK, 70, 0, 0),
						(Attr.NOW_TP, 30, 0, 0),
						(Attr.NOW_HEALTH, -150, 0, 0,)],
				}
			},
			{
				"name":"暗影吮吸",
				"text":"对目标及其半径3内的敌人造成60(+0.7自身攻击力)真实伤害，并将所造成伤害的30%转换为生命值",
				"tp_cost":20,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[],

				"effect":{
					EFFECT_HURT:(60, Attr.ATTACK, 0, 0.7, True),
					EFFECT_AOE:(3, False),
					EFFECT_LIFESTEAL:0.30,
				}
			},
			{
				"name":"闪电之枪",
				"text":"对目标及其半径4范围内自己以外的玩家造成70(+2.0自身攻击力)真实伤害，并将所造成伤害的10%转换为生命值",
				"tp_cost":50,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[],

				"effect":{
					EFFECT_AOE:(4, False),
					EFFECT_HURT:(70, Attr.ATTACK, 0, 2.0, True),
					EFFECT_LIFESTEAL:0.1,
				}
			}
		],
		"passive_skills": []
	},
	1020:{
		"name":"美美",
		"health":1000,
		"distance":5,
		"attack":110,
		"defensive":80,
		"crit":5,
		"tp":0,

		"active_skills" : [
			{
				"name":"普通攻击",
				"text":"对目标造成0(+1.0自身攻击力)伤害",
				"tp_cost":0,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[],

				"effect":{
					EFFECT_HURT:(0, Attr.ATTACK, 0, 1, False)
				}
			},
			{
				"name":"蹦蹦跳跳",
				"text":"自身增加40点攻击力和20点防御力",
				"tp_cost":20,
				"trigger": TRIGGER_ME,
				"passive":[],

				"effect":{
					EFFECT_ATTR_CHANGE:[
						(Attr.ATTACK, 40, 0, 0),
						(Attr.DEFENSIVE, 20, 0, 0)],
				}
			},
			{
				"name":"崩山击",
				"text":"向目标移动3格，并对目标及其半径4范围内的所有玩家造成100(+1.0自身攻击力)伤害",
				"tp_cost":30,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[0],

				"effect":{
					EFFECT_HURT:(100, Attr.ATTACK, 0, 1.0, False),
					EFFECT_AOE:(4, False)
				}
			},
			{
				"name":"兰德索尔正义",
				"text":"对目标造成100点真实伤害，目标当前生命值每降低1%则额外造成7点真实伤害",#斩杀效果
				"tp_cost":65,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[],

				"effect":{
					EFFECT_HURT:(100, Attr.ATTACK, 0, 0, True),
					EFFECT_ELIMINATE:(1, 7)
				}
			},
		],
		"passive_skills": [
			{
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"effect":{
					EFFECT_MOVE_GOAL:(3, False),
				}
			}
		]
	},
	1016:{
		"name":"铃奈",
		"health":900,
		"distance":12,
		"attack":100,
		"defensive":50,
		"crit":0,
		"tp":0,

		"active_skills" : [
			{
				"name":"普通攻击",
				"text":"对目标造成0(+1.0自身攻击力)伤害",
				"tp_cost":10,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[],

				"effect":{
					EFFECT_HURT:(0, Attr.ATTACK, 0, 1, False)
				}
			},
			{
				"name":"魅力全开",
				"text":"每自我回合增加15%暴击率，持续全局",
				"tp_cost":0,
				"trigger": TRIGGER_ME,
				"passive":[],

				"effect":{
					EFFECT_BUFF:[(BuffType.TurnSelfAttrCritUp, 15, 9999)],
				}
			},
			{
				"name":"会心飞镖",
				"text":"对目标造成100(+1.0自身攻击力)伤害",
				"tp_cost":20,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[],

				"effect":{
					EFFECT_HURT:(100, Attr.ATTACK, 0, 1.0, False)
				}
			},
			{
				"name":"一箭穿心",
				"text":"对目标造成200(+2.0自身攻击力)伤害",
				"tp_cost":70,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[],

				"effect":{
					EFFECT_HURT:(200, Attr.ATTACK, 0, 2.0, True)
				}
			},
		],
		"passive_skills": []
	},
	1006:{
		"name":"茜里",
		"health":1000,
		"distance":10,
		"attack":90,
		"defensive":80,
		"crit":5,
		"tp":0,

		"active_skills" : [
			{
				"name":"普通攻击",
				"text":"对目标造成0(+1.0自身攻击力)伤害",
				"tp_cost":10,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[],

				"effect":{
					EFFECT_HURT:(0, Attr.ATTACK, 0, 1, False)
				}
			},
			{
				"name":"小恶魔之吻",
				"text":"对目标造成100(+1.0自身攻击力)伤害，并将所造成伤害的50%转换为生命值",
				"tp_cost":20,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[],

				"effect":{
					EFFECT_HURT:(100, Attr.ATTACK, 0, 1.0, False),
					EFFECT_LIFESTEAL:0.5,
				}
			},
			{
				"name":"暗影打击",
				"text":"对目标造成100(+1.0自身攻击力)伤害，并降低目标35点护甲持续12回合",
				"tp_cost":20,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[],

				"effect":{
					EFFECT_HURT:(100, Attr.ATTACK, 0, 1.0, False),
					EFFECT_BUFF:[(BuffType.NormalAttrDefDown, -35, 12)],
				}
			},
			{
				"name":"甜蜜恶魔声援",
				"text":"自身增加200点攻击力，持续1回合，并继续下一回合",
				"tp_cost":50,
				"trigger": TRIGGER_ME,
				"passive":[],

				"effect":{
					EFFECT_BUFF:[(BuffType.NormalAttrAtkUp, 200, 1)],
					EFFECT_LOCKTURN:1,
				}
			}
		],
		"passive_skills": []
	},
	1004:{
		"name":"未奏希",
		"health":1200,
		"distance":10,
		"attack":100,
		"defensive":175,
		"crit":10,
		"tp":0,

		"active_skills" : [
			{
				"name":"普通攻击",
				"text":"对目标造成0(+1.0自身攻击力)伤害",
				"tp_cost":10,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[],

				"effect":{
					EFFECT_HURT:(0, Attr.ATTACK, 0, 1, False)
				}
			},
			{
				"name":"小炸弹",
				"text":"对目标及其半径4范围内的所有玩家造成100(+1.0自身攻击力)伤害（不包括自己）",
				"tp_cost":20,
				"trigger": TRIGGER_SELECT,
				"passive":[],

				"effect":{
					EFFECT_HURT:(100, Attr.ATTACK, 0, 1.0, False),
					EFFECT_AOE:(4, False)
				}
			},
			{
				"name":"中炸弹",
				"text":"对目标及其半径8范围内的所有玩家造成150(+1.5自身攻击力)伤害（包括自己）",
				"tp_cost":40,
				"trigger": TRIGGER_SELECT,
				"passive":[],

				"effect":{
					EFFECT_HURT:(150, Attr.ATTACK, 0, 1.5, False),
					EFFECT_AOE:(8, True)
				}
			},
			{
				"name":"大炸弹",
				"text":"对场上所有玩家造成200(+2.0自身攻击力)伤害（包括自己），并赋予其他玩家灼烧状态",
				"tp_cost":60,
				"trigger": TRIGGER_ALL,
				"passive":[0],

				"effect":{
					EFFECT_HURT:(200, Attr.ATTACK, 0, 2.0, False)
				}
			}
		],
		"passive_skills": [
			{
				"trigger": TRIGGER_ALL_EXCEPT_ME,
				"effect":{
					EFFECT_BUFF:[(BuffType.TurnAttrHelDown2, -100, 3)],
				}
			}
		]
	},
	1003:{
		"name":"怜",
		"health":900,
		"distance":5,
		"attack":100,
		"defensive":70,
		"crit":5,
		"tp":0,

		"active_skills" : [
			{
				"name":"普通攻击",
				"text":"对目标造成0(+1.0自身攻击力)伤害",
				"tp_cost":0,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[],

				"effect":{
					EFFECT_HURT:(0, Attr.ATTACK, 0, 1, False)
				}
			},
			{
				"name":"破甲突刺",
				"text":"无视距离，对离自己最近的目标造成100(+1.0自身攻击力)伤害，并降低目标20点防御力",
				"tp_cost":20,
				"trigger": TRIGGER_NEAR,
				"passive":[],

				"effect":{
					EFFECT_HURT:(100, Attr.ATTACK, 0, 1.0, False),
					EFFECT_ATTR_CHANGE:[(Attr.DEFENSIVE, -20, 0, 0)],
				}
			},
			{
				"name":"格挡",
				"text":"为自己增加一个200点生命值的护盾（只可触发1次），并增加30点攻击力",
				"tp_cost":30,
				"trigger": TRIGGER_ME,
				"passive":[],

				"effect":{
					EFFECT_BUFF:[(BuffType.Shield, 200, 1)],
					EFFECT_ATTR_CHANGE:[(Attr.ATTACK, 30, 0, 0)],
				}
			},
			{
				"name":"极·鬼剑术-暴风式",
				"text":"对自己以外的所有人造成200(+1.0自身攻击力)真实伤害",
				"tp_cost":60,
				"trigger": TRIGGER_ALL_EXCEPT_ME,
				"passive":[],

				"effect":{
					EFFECT_HURT:(200, Attr.ATTACK, 0, 1.0, True)
				}
			}
		],
		"passive_skills": []
	},
	1002:{
		"name":"优衣",
		"health":850,
		"distance":8,
		"attack":80,
		"defensive":60,
		"crit":0,
		"tp":10,

		"active_skills" : [
			{
				"name":"普通攻击",
				"text":"对目标造成0(+1.0自身攻击力)伤害",
				"tp_cost":0,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[],

				"effect":{
					EFFECT_HURT:(0, Attr.ATTACK, 0, 1, False)
				}
			},
			{
				"name":"花瓣射击",
				"text":"对目标造成75(+1.5自身攻击力)伤害，并降低目标70点攻击力1回合和10点TP",
				"tp_cost":20,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[],

				"effect":{
					EFFECT_HURT:(75, Attr.ATTACK, 0, 1.5, False),
					EFFECT_BUFF:[(BuffType.NormalSelfAttrAtkDown, -70, 1)],
					EFFECT_ATTR_CHANGE:[
						(Attr.NOW_TP, -10, 0, 0)],
				}
			},
			{
				"name":"全体治愈",
				"text":"全体回复100生命值，自己额外回复300生命值，除自己外减少3点攻击距离",
				"tp_cost":60,
				"trigger": TRIGGER_ALL,
				"passive":[0,1],

				"effect":{
					EFFECT_ATTR_CHANGE:[(Attr.NOW_HEALTH, 100, 0, 0)]
				}
			}
		],
		"passive_skills": [
			{
				"trigger": TRIGGER_ALL_EXCEPT_ME,
				"effect":{
					EFFECT_ATTR_CHANGE:[(Attr.DISTANCE, -3, 0, 0)],
				}
			},
			{
				"trigger": TRIGGER_ME,
				"effect":{
					EFFECT_ATTR_CHANGE:[(Attr.NOW_HEALTH, 300, 0, 0)]
				}
			}
		],
	},
	1001:{
		"name":"日和莉",
		"health":900,
		"distance":5,
		"attack":100,
		"defensive":60,
		"crit":10,
		"tp":0,

		"active_skills" : [
			{
				"name":"普通攻击",
				"text":"对目标造成0(+1.0自身攻击力)伤害",
				"tp_cost":0,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[],

				"effect":{
					EFFECT_HURT:(0, Attr.ATTACK, 0, 1, False)
				}
			},
			{
				"name":"勇气迸发",
				"text":"自身增加50点攻击力和1点攻击距离",
				"tp_cost":20,
				"trigger": TRIGGER_ME,
				"passive":[],

				"effect":{
					EFFECT_ATTR_CHANGE:[
						(Attr.ATTACK, 50, 0, 0),
						(Attr.DISTANCE, 1, 0, 0)],
				}
			},
			{
				"name":"日和莉烈焰冲击",
				"text":"对目标造成300(+2.0自身攻击力)伤害，若目标被击倒，自身回复70点tp并继续下一回合",
				"tp_cost":100,
				"trigger": TRIGGER_SELECT_EXCEPT_ME,
				"passive":[],

				"effect":{
					EFFECT_HURT:(300, Attr.ATTACK, 0, 2, False),
					EFFECT_OUT_TP:70,
					EFFECT_OUT_LOCKTURN:1
				}
			}
		],
		"passive_skills": []
	},
}