/**
 * Gamification UI Integration
 *
 * Handles display and interaction for badges, achievements, and progress tracking
 * Integrates with existing Flask templates and localStorage patterns
 */

class GamificationUI {
  constructor() {
    this.achievements = this.loadAchievements();
    this.progress = this.loadProgress();
    this.notifications = [];
    this.initializeUI();
  }

  /**
   * Load achievements from localStorage
   */
  loadAchievements() {
    try {
      const data = localStorage.getItem("user_achievements");
      return data
        ? JSON.parse(data)
        : {
            badges: {
              analysis_milestones: [],
              pattern_mastery: [],
              research_excellence: [],
              community_contributions: [],
              learning_streaks: [],
              stage_progressions: [],
            },
            progress: {
              analysis_count: 0,
              current_streak: 0,
              best_streak: 0,
              total_session_time: 0,
              skill_competencies: {
                debt_analysis: 0.0,
                growth_indicators: 0.0,
                value_assessment: 0.0,
              },
              stage_progression_points: 0,
            },
            statistics: {
              total_badges: 0,
              total_achievement_points: 0,
              days_active: 1,
              average_session_time: 0,
            },
          };
    } catch (error) {
      console.error("Error loading achievements:", error);
      return this.getDefaultAchievements();
    }
  }

  /**
   * Load progress metrics from localStorage
   */
  loadProgress() {
    try {
      const data = localStorage.getItem("user_progress");
      return data
        ? JSON.parse(data)
        : {
            analysis_count: 0,
            pattern_recognition_score: 0.0,
            research_engagement_score: 0.0,
            community_contribution_score: 0.0,
            current_streak: 0,
            best_streak: 0,
            last_active_date: null,
            total_session_time: 0.0,
            stage_progression_points: 0.0,
            skill_competencies: {
              debt_analysis: 0.0,
              growth_indicators: 0.0,
              value_assessment: 0.0,
            },
          };
    } catch (error) {
      console.error("Error loading progress:", error);
      return this.getDefaultProgress();
    }
  }

  /**
   * Initialize gamification UI components
   */
  initializeUI() {
    this.createProgressIndicators();
    this.createBadgeShowcase();
    this.createStreakCounter();
    this.updateAchievementDisplay();
    this.checkForNewAchievements();
  }

  /**
   * Create progress indicators in the UI
   */
  createProgressIndicators() {
    const progressContainer = document.getElementById("progress-indicators");
    if (!progressContainer) return;

    const competencies = this.progress.skill_competencies;

    const progressHTML = `
            <div class="progress-section">
                <h3>Learning Progress</h3>
                
                <div class="skill-progress">
                    <label>Debt Analysis Mastery</label>
                    <div class="progress-bar">
                        <div class="progress-fill debt-analysis" style="width: ${
                          competencies.debt_analysis * 100
                        }%"></div>
                        <span class="progress-text">${Math.round(
                          competencies.debt_analysis * 100
                        )}%</span>
                    </div>
                </div>
                
                <div class="skill-progress">
                    <label>Growth Indicators Mastery</label>
                    <div class="progress-bar">
                        <div class="progress-fill growth-indicators" style="width: ${
                          competencies.growth_indicators * 100
                        }%"></div>
                        <span class="progress-text">${Math.round(
                          competencies.growth_indicators * 100
                        )}%</span>
                    </div>
                </div>
                
                <div class="skill-progress">
                    <label>Value Assessment Mastery</label>
                    <div class="progress-bar">
                        <div class="progress-fill value-assessment" style="width: ${
                          competencies.value_assessment * 100
                        }%"></div>
                        <span class="progress-text">${Math.round(
                          competencies.value_assessment * 100
                        )}%</span>
                    </div>
                </div>
                
                <div class="overall-stats">
                    <div class="stat-item">
                        <span class="stat-value">${
                          this.progress.analysis_count
                        }</span>
                        <span class="stat-label">Analyses Completed</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">${Math.round(
                          this.progress.total_session_time / 3600
                        )}h</span>
                        <span class="stat-label">Total Learning Time</span>
                    </div>
                </div>
            </div>
        `;

    progressContainer.innerHTML = progressHTML;
  }

  /**
   * Create badge showcase display
   */
  createBadgeShowcase() {
    const badgeContainer = document.getElementById("badge-showcase");
    if (!badgeContainer) return;

    let badgeHTML = '<div class="badge-showcase"><h3>Achievements</h3>';

    // Group badges by category
    const categories = [
      { key: "analysis_milestones", title: "Analysis Milestones" },
      { key: "pattern_mastery", title: "Pattern Mastery" },
      { key: "learning_streaks", title: "Learning Streaks" },
      { key: "research_excellence", title: "Research Excellence" },
      { key: "community_contributions", title: "Community Contributions" },
    ];

    categories.forEach((category) => {
      const badges = this.achievements.badges[category.key] || [];
      if (badges.length > 0) {
        badgeHTML += `
                    <div class="badge-category">
                        <h4>${category.title}</h4>
                        <div class="badge-grid">
                `;

        badges.forEach((badge) => {
          badgeHTML += `
                        <div class="badge-item earned" data-badge="${
                          badge.badge_type
                        }">
                            <div class="badge-icon">${this.getBadgeIcon(
                              badge.badge_type
                            )}</div>
                            <div class="badge-info">
                                <div class="badge-name">${
                                  badge.display_name
                                }</div>
                                <div class="badge-description">${
                                  badge.description
                                }</div>
                                <div class="badge-date">Earned: ${
                                  badge.earned_date
                                }</div>
                            </div>
                        </div>
                    `;
        });

        badgeHTML += "</div></div>";
      }
    });

    badgeHTML += "</div>";
    badgeContainer.innerHTML = badgeHTML;
  }

  /**
   * Create learning streak counter
   */
  createStreakCounter() {
    const streakContainer = document.getElementById("streak-counter");
    if (!streakContainer) return;

    const streakHTML = `
            <div class="streak-display">
                <div class="streak-counter">
                    <div class="streak-flame">🔥</div>
                    <div class="streak-info">
                        <div class="streak-current">${
                          this.progress.current_streak
                        }</div>
                        <div class="streak-label">Day Streak</div>
                        <div class="streak-best">Best: ${
                          this.progress.best_streak
                        } days</div>
                    </div>
                </div>
                <div class="streak-encouragement">
                    ${this.getStreakEncouragement()}
                </div>
            </div>
        `;

    streakContainer.innerHTML = streakHTML;
  }

  /**
   * Get icon for badge type
   */
  getBadgeIcon(badgeType) {
    const icons = {
      first_analysis: "🎯",
      bronze_analyst: "🥉",
      silver_analyst: "🥈",
      gold_analyst: "🥇",
      platinum_analyst: "💎",
      debt_detective: "🔍",
      growth_spotter: "📈",
      value_hunter: "💰",
      pattern_master: "🧠",
      consistent_learner: "⭐",
      dedicated_student: "🌟",
      learning_champion: "👑",
    };
    return icons[badgeType] || "🏆";
  }

  /**
   * Get streak encouragement message
   */
  getStreakEncouragement() {
    const streak = this.progress.current_streak;

    if (streak === 0) {
      return "Start your learning journey today!";
    } else if (streak < 7) {
      return `${7 - streak} more days to earn Consistent Learner badge!`;
    } else if (streak < 30) {
      return `${30 - streak} more days to earn Dedicated Student badge!`;
    } else if (streak < 90) {
      return `${90 - streak} more days to earn Learning Champion badge!`;
    } else {
      return "Amazing dedication! You're a true Learning Champion!";
    }
  }

  /**
   * Update achievement display
   */
  updateAchievementDisplay() {
    // Update stats in header or sidebar
    const statsElements = {
      "total-badges": this.achievements.statistics.total_badges,
      "achievement-points":
        this.achievements.statistics.total_achievement_points,
      "current-streak": this.progress.current_streak,
    };

    Object.entries(statsElements).forEach(([id, value]) => {
      const element = document.getElementById(id);
      if (element) {
        element.textContent = value;
      }
    });
  }

  /**
   * Check for new achievements and show notifications
   */
  checkForNewAchievements() {
    const newAchievements = localStorage.getItem("new_achievements");
    if (newAchievements) {
      try {
        const achievements = JSON.parse(newAchievements);
        achievements.forEach((achievement) => {
          this.showAchievementNotification(achievement);
        });
        // Clear notifications after showing
        localStorage.removeItem("new_achievements");
      } catch (error) {
        console.error("Error processing new achievements:", error);
      }
    }
  }

  /**
   * Show achievement notification
   */
  showAchievementNotification(achievement) {
    const notification = document.createElement("div");
    notification.className = "achievement-notification";
    notification.innerHTML = `
            <div class="notification-content">
                <div class="notification-icon">${this.getBadgeIcon(
                  achievement.badge_type
                )}</div>
                <div class="notification-text">
                    <div class="notification-title">Achievement Unlocked!</div>
                    <div class="notification-badge">${
                      achievement.display_name
                    }</div>
                    <div class="notification-description">${
                      achievement.description
                    }</div>
                </div>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;

    document.body.appendChild(notification);

    // Auto-remove after 5 seconds
    setTimeout(() => {
      if (notification.parentElement) {
        notification.remove();
      }
    }, 5000);

    // Add entrance animation
    setTimeout(() => {
      notification.classList.add("show");
    }, 100);
  }

  /**
   * Update progress when user completes an activity
   */
  updateProgress(activityData) {
    // Update local progress
    if (activityData.analysis_completed) {
      this.progress.analysis_count += 1;
    }

    if (activityData.skill_improvements) {
      Object.entries(activityData.skill_improvements).forEach(
        ([skill, improvement]) => {
          if (this.progress.skill_competencies[skill] !== undefined) {
            this.progress.skill_competencies[skill] = Math.min(
              1.0,
              this.progress.skill_competencies[skill] + improvement
            );
          }
        }
      );
    }

    // Update streak
    this.updateLearningStreak();

    // Save to localStorage
    this.saveProgress();

    // Refresh UI
    this.initializeUI();
  }

  /**
   * Update learning streak
   */
  updateLearningStreak() {
    const today = new Date().toISOString().split("T")[0];

    if (this.progress.last_active_date) {
      const lastDate = new Date(this.progress.last_active_date);
      const todayDate = new Date(today);
      const daysDiff = Math.floor(
        (todayDate - lastDate) / (1000 * 60 * 60 * 24)
      );

      if (daysDiff === 1) {
        this.progress.current_streak += 1;
        this.progress.best_streak = Math.max(
          this.progress.best_streak,
          this.progress.current_streak
        );
      } else if (daysDiff > 1) {
        this.progress.current_streak = 1;
      }
    } else {
      this.progress.current_streak = 1;
      this.progress.best_streak = 1;
    }

    this.progress.last_active_date = today;
  }

  /**
   * Save progress to localStorage
   */
  saveProgress() {
    try {
      localStorage.setItem("user_progress", JSON.stringify(this.progress));
    } catch (error) {
      console.error("Error saving progress:", error);
    }
  }

  /**
   * Save achievements to localStorage
   */
  saveAchievements() {
    try {
      localStorage.setItem(
        "user_achievements",
        JSON.stringify(this.achievements)
      );
    } catch (error) {
      console.error("Error saving achievements:", error);
    }
  }

  /**
   * Get default achievements structure
   */
  getDefaultAchievements() {
    return {
      badges: {
        analysis_milestones: [],
        pattern_mastery: [],
        research_excellence: [],
        community_contributions: [],
        learning_streaks: [],
        stage_progressions: [],
      },
      progress: {
        analysis_count: 0,
        current_streak: 0,
        best_streak: 0,
        total_session_time: 0,
        skill_competencies: {
          debt_analysis: 0.0,
          growth_indicators: 0.0,
          value_assessment: 0.0,
        },
        stage_progression_points: 0,
      },
      statistics: {
        total_badges: 0,
        total_achievement_points: 0,
        days_active: 1,
        average_session_time: 0,
      },
    };
  }

  /**
   * Get default progress structure
   */
  getDefaultProgress() {
    return {
      analysis_count: 0,
      pattern_recognition_score: 0.0,
      research_engagement_score: 0.0,
      community_contribution_score: 0.0,
      current_streak: 0,
      best_streak: 0,
      last_active_date: null,
      total_session_time: 0.0,
      stage_progression_points: 0.0,
      skill_competencies: {
        debt_analysis: 0.0,
        growth_indicators: 0.0,
        value_assessment: 0.0,
      },
    };
  }
}

// Initialize gamification UI when DOM is ready
document.addEventListener("DOMContentLoaded", function () {
  if (typeof window.gamificationUI === "undefined") {
    window.gamificationUI = new GamificationUI();
  }
});

// Export for use in other modules
if (typeof module !== "undefined" && module.exports) {
  module.exports = GamificationUI;
}
