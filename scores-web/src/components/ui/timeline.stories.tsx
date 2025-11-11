import type { Meta, StoryObj } from "@storybook/nextjs";

import { Timeline } from "@/components/ui/timeline";

const meta: Meta<typeof Timeline> = {
  title: "Components/Timeline",
  component: Timeline,
  args: {
    items: [
      {
        id: "event-1",
        timeLabel: "12:04",
        title: "Goal — Joanna Silva",
        description: "Assist from Kowalska, smooth endzone offence.",
        teamName: "Sky This",
        tone: "goal",
      },
      {
        id: "event-2",
        timeLabel: "11:42",
        title: "Turnover — Layout block",
        description: "Piotr Nowak with the layout D at midfield.",
        teamName: "4Hands",
        tone: "turnover",
      },
      {
        id: "event-3",
        timeLabel: "10:10",
        title: "Timeout — Team",
        description: "Sky This takes a timeout near the endzone.",
        teamName: "Sky This",
        tone: "timeout",
      },
    ],
  },
};

export default meta;

type Story = StoryObj<typeof Timeline>;

export const Default: Story = {};

