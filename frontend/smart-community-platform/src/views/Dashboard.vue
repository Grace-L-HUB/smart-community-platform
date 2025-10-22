<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// 模拟数据 - 统计信息
const statistics = ref({
  residents: 256,
  buildings: 12,
  units: 48,
  complaints: 8
});

// 模拟数据 - 最近活动
const recentActivities = ref([
  {
    id: 1,
    title: '物业费缴纳提醒',
    description: '3栋2单元业主物业费即将到期',
    time: '2023-11-01 10:30',
    type: 'reminder'
  },
  {
    id: 2,
    title: '社区活动通知',
    description: '周末将举办秋季社区运动会',
    time: '2023-10-31 16:45',
    type: 'event'
  },
  {
    id: 3,
    title: '设备维修完成',
    description: '小区东门门禁系统已修复',
    time: '2023-10-31 09:20',
    type: 'maintenance'
  },
  {
    id: 4,
    title: '新业主入住',
    description: '5栋1单元新业主已完成入住登记',
    time: '2023-10-30 14:15',
    type: 'new_resident'
  }
]);

// 快捷操作数据
const quickActions = ref([
  { title: '住户管理', icon: 'mdi-account-group', color: 'primary', route: '/owners' },
  { title: '房产管理', icon: 'mdi-home', color: 'secondary', route: '/properties' },
  { title: '投诉处理', icon: 'mdi-comment-alert', color: 'error', route: '/complaints' },
  { title: '公告发布', icon: 'mdi-bullhorn', color: 'success', route: '/announcements' }
]);

// 根据类型获取活动图标
const getActivityIcon = (type: string) => {
  switch (type) {
    case 'reminder': return 'mdi-bell-outline';
    case 'event': return 'mdi-calendar';
    case 'maintenance': return 'mdi-wrench';
    case 'new_resident': return 'mdi-account-plus';
    default: return 'mdi-alert-circle-outline';
  }
};

// 根据类型获取活动图标颜色
const getActivityIconColor = (type: string) => {
  switch (type) {
    case 'reminder': return 'amber';
    case 'event': return 'primary';
    case 'maintenance': return 'success';
    case 'new_resident': return 'info';
    default: return 'grey';
  }
};

// 获取统计标签
const getStatLabel = (key: string) => {
  const labels: Record<string, string> = {
    residents: '住户总数',
    buildings: '楼栋数',
    units: '单元数',
    complaints: '待处理投诉'
  };
  return labels[key] || key;
};

// 处理快捷操作
const handleQuickAction = (action: any) => {
  // 这里可以根据需要添加路由跳转逻辑
  console.log('Quick action clicked:', action.title);
};

// 检查登录状态
onMounted(() => {
  const token = localStorage.getItem('token');
  if (!token) {
    router.push('/');
  }
});

// 退出登录
const handleLogout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  router.push('/');
};

// 获取当前用户信息
const currentUser = ref({
  username: localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user') || '{}').username : '管理员',
  avatar: 'mdi-account-circle'
});
</script>

<template>
  <v-app class="dashboard-container">
    <!-- 顶部导航栏 -->
    <v-app-bar
      color="primary"
      dark
      app
      dense
    >
      <v-app-bar-title>智慧社区管理平台</v-app-bar-title>
      <v-spacer></v-spacer>
      <v-menu offset-y>
        <template v-slot:activator="{ props }">
          <v-btn
            v-bind="props"
            icon
            class="user-avatar"
          >
            <v-avatar>
              <v-icon size="32">{{ currentUser.avatar }}</v-icon>
            </v-avatar>
          </v-btn>
        </template>
        <v-list>
          <v-list-item>
            <v-list-item-title>{{ currentUser.username }}</v-list-item-title>
          </v-list-item>
          <v-divider></v-divider>
          <v-list-item @click="handleLogout">
            <v-list-item-icon>
              <v-icon>mdi-logout</v-icon>
            </v-list-item-icon>
            <v-list-item-title>退出登录</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>

    <!-- 主要内容区域 -->
    <v-main class="py-6 px-4">
      <v-container>
        <!-- 欢迎消息 -->
        <v-card elevation="0" class="mb-6">
          <v-card-text class="text-h5">
            欢迎回来，{{ currentUser.username }}！
          </v-card-text>
        </v-card>

        <!-- 数据统计卡片 -->
        <v-row class="mb-8">
          <v-col cols="12" sm="6" md="3" v-for="(value, key) in statistics" :key="key">
            <v-card class="stat-card" elevation="2">
              <v-card-text>
                <div class="stat-label">{{ getStatLabel(key) }}</div>
                <div class="stat-value text-h4 font-bold">{{ value }}</div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- 最近活动 -->
        <v-card class="mb-6" elevation="2">
          <v-card-title>
            <v-icon left>mdi-history</v-icon>
            最近活动
          </v-card-title>
          <v-divider></v-divider>
          <v-card-text>
            <v-list>
              <v-list-item v-for="activity in recentActivities" :key="activity.id">
                <v-list-item-avatar>
                  <v-icon :color="getActivityIconColor(activity.type)">{{ getActivityIcon(activity.type) }}</v-icon>
                </v-list-item-avatar>
                <v-list-item-content>
                  <v-list-item-title>{{ activity.title }}</v-list-item-title>
                  <v-list-item-subtitle>{{ activity.description }}</v-list-item-subtitle>
                </v-list-item-content>
                <v-list-item-action>
                  <span class="text-sm text-grey">{{ activity.time }}</span>
                </v-list-item-action>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>

        <!-- 快捷操作 -->
        <v-card elevation="2">
          <v-card-title>
            <v-icon left>mdi-lightning-bolt</v-icon>
            快捷操作
          </v-card-title>
          <v-divider></v-divider>
          <v-card-text>
            <v-row>
              <v-col cols="6" sm="4" md="3" v-for="action in quickActions" :key="action.title">
                <v-card @click="handleQuickAction(action)" class="action-card cursor-pointer hoverable">
                  <v-card-text class="text-center">
                    <v-icon :color="action.color" size="40">{{ action.icon }}</v-icon>
                    <div class="mt-2">{{ action.title }}</div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-container>
    </v-main>
  </v-app>
</template>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  background-color: #f5f5f5;
  display: flex;
  flex-direction: column;
}

.stat-card {
  height: 100%;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-label {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 8px;
}

.stat-value {
  color: #1976d2;
  font-weight: bold;
}

.action-card {
  height: 100%;
  transition: all 0.2s;
  cursor: pointer;
}

.action-card:hover {
  background-color: #f0f0f0;
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
}

.hoverable {
  transition: all 0.3s ease;
}

.hoverable:hover {
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}

.user-avatar {
  min-width: 50px;
  margin-right: 10px;
}

@media (max-width: 600px) {
  .stat-card, .action-card {
    margin-bottom: 1rem;
  }
}
</style>