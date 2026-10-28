<template>
  <div class="skeleton-wrapper">
    <!-- Stats Skeleton -->
    <div class="skeleton-stats-grid">
      <div v-for="i in 6" :key="i" class="skeleton-stat-card">
        <div class="skeleton-line w-20" />
        <div class="skeleton-block" />
        <div class="skeleton-line w-30" />
      </div>
    </div>

    <!-- Table Skeleton -->
    <div class="skeleton-table-card">
      <div class="skeleton-toolbar">
        <div class="skeleton-input" />
        <div class="skeleton-btn" />
      </div>
      <div class="skeleton-rows">
        <div v-for="j in 5" :key="j" class="skeleton-row">
          <div class="skeleton-cell w-25" />
          <div class="skeleton-cell w-15" />
          <div class="skeleton-cell w-20" />
          <div class="skeleton-cell w-15" />
          <div class="skeleton-cell w-10" />
          <div class="skeleton-cell w-15" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.skeleton-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
}

.skeleton-stats-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 0.875rem;
}

.skeleton-stat-card {
  padding: 1rem;
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.skeleton-line {
  height: 12px;
  background: #e2e8f0;
  border-radius: 4px;
  animation: pulse 1.5s infinite ease-in-out;
}

.skeleton-block {
  height: 28px;
  width: 50px;
  background: #cbd5e1;
  border-radius: 6px;
  animation: pulse 1.5s infinite ease-in-out;
}

.skeleton-table-card {
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.skeleton-toolbar {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.skeleton-input {
  height: 38px;
  width: 250px;
  background: #e2e8f0;
  border-radius: 6px;
  animation: pulse 1.5s infinite ease-in-out;
}

.skeleton-btn {
  height: 38px;
  width: 100px;
  background: #e2e8f0;
  border-radius: 6px;
  animation: pulse 1.5s infinite ease-in-out;
}

.skeleton-rows {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.skeleton-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid #f1f5f9;
}

.skeleton-cell {
  height: 16px;
  background: #f1f5f9;
  border-radius: 4px;
  animation: pulse 1.5s infinite ease-in-out;
}

.w-10 { width: 10%; }
.w-15 { width: 15%; }
.w-20 { width: 20%; }
.w-25 { width: 25%; }
.w-30 { width: 30%; }

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.45; }
}

@media (max-width: 1200px) {
  .skeleton-stats-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .skeleton-stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
