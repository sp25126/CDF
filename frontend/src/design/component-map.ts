/**
 * Component Map for Shiksha Sahayak
 * Links logical components to their visual zones.
 */

export const componentMap = {
  TopContextBar: {
    items: ["TopicTitle", "ModeIndicator", "LanguageBadge", "JuliStateLabel"],
  },
  TeachingCanvas: {
    zones: {
      avatar: {
        components: ["AvatarCanvas", "AvatarSync"],
        priority: "high",
      },
      content: {
        components: ["ResponseRenderer", "QuizCard", "ClarificationState"],
        priority: "dominant",
      },
      media: {
        components: ["VisualCards", "VideoCards", "MediaRail"],
        priority: "supporting",
      },
    },
  },
  TeacherConsole: {
    zones: {
      controls: {
        components: ["VoiceTrigger", "ModeSwitcher", "HandsFreeToggle"],
      },
      suggestions: {
        components: ["NextActions", "SourceChips"],
      },
    },
  },
};
