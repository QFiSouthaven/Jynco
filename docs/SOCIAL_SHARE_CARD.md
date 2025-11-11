# Social Share Card Design

Create professional social media cards for sharing Video Foundry.

## Dimensions

### Primary Card (Twitter/X, LinkedIn, Facebook)
- **Size**: 1200 x 630 px
- **Aspect Ratio**: 1.91:1
- **Format**: PNG or JPG
- **File name**: `video-foundry-social-card.png`

### GitHub Social Preview
- **Size**: 1280 x 640 px
- **Format**: PNG
- **Location**: Repository Settings → Social Preview

## Design Specifications

### Layout
```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  [Logo/Icon]               VIDEO FOUNDRY          │
│     🎬                                              │
│                                                     │
│         Scalable AI Video Generation Pipeline      │
│                                                     │
│  ┌──────┐ ┌──────┐ ┌──────┐                       │
│  │Seg 1 │ │Seg 2 │ │Seg 3 │  ← Timeline Visual   │
│  └──────┘ └──────┘ └──────┘                       │
│                                                     │
│  ✨ Timeline Editor  🚀 Intelligent Re-rendering  │
│  🔌 Multi-Model     ⚡ Real-Time Progress         │
│                                                     │
│  github.com/QFiSouthaven/Jynco                    │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Color Scheme

**Option 1: Dark Theme** (Recommended)
- Background: `#0f0f0f` (Dark gray)
- Primary Text: `#ffffff` (White)
- Secondary Text: `#a0a0a0` (Light gray)
- Accent: `#3b82f6` (Blue) for highlights
- Border: `#2d3748` (Dark blue-gray)

**Option 2: Gradient Theme**
- Background: Linear gradient from `#1e3a8a` to `#0f172a` (Blue to dark)
- Text: `#ffffff` (White)
- Accents: `#60a5fa` (Light blue)

**Option 3: Tech Theme**
- Background: `#0a0e1e` (Very dark blue)
- Primary: `#00d9ff` (Cyan)
- Secondary: `#ff006e` (Pink)
- Text: `#ffffff` (White)

### Typography

**Title Font**
- Font: Inter Bold or SF Pro Display Bold
- Size: 72px
- Weight: 700
- Color: White
- Letter spacing: -2px

**Subtitle Font**
- Font: Inter Regular or SF Pro Display Regular
- Size: 36px
- Weight: 400
- Color: #a0a0a0

**Feature List**
- Font: Inter Medium
- Size: 24px
- Weight: 500
- Color: White

**URL**
- Font: JetBrains Mono or Menlo
- Size: 20px
- Weight: 400
- Color: #60a5fa

### Visual Elements

**1. Logo/Icon**
- Film reel 🎬 or video camera icon
- Size: 120x120px
- Position: Top left, 60px from edges

**2. Timeline Visualization**
- 3-5 segment boxes showing timeline concept
- Each box: 150x80px with 20px spacing
- Subtle gradient or border
- Label: "Segment 1", "Segment 2", etc.

**3. Feature Icons**
- Use emoji or simple icons
- Size: 32x32px
- Spacing: 40px between features

**4. Background Pattern** (Optional)
- Subtle grid or dot pattern
- Opacity: 5-10%
- Color: White or accent color

## Creating the Card

### Option 1: Figma (Recommended)

1. **Create artboard**: 1200 x 630 px
2. **Import template**: Use provided specifications
3. **Add elements**: Follow layout above
4. **Export**: PNG at 2x resolution for crisp display

**Figma Template**: [Available in repo - coming soon]

### Option 2: Canva (Easiest)

1. Go to Canva.com
2. Create custom size: 1200 x 630 px
3. Use "Dark Modern" templates
4. Replace text with Video Foundry content
5. Download as PNG

### Option 3: Code (HTML/CSS)

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    body {
      margin: 0;
      padding: 0;
      width: 1200px;
      height: 630px;
      background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%);
      font-family: 'Inter', sans-serif;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
    }
    .container {
      text-align: center;
      padding: 40px;
    }
    .title {
      font-size: 72px;
      font-weight: 700;
      margin: 0;
      letter-spacing: -2px;
    }
    .subtitle {
      font-size: 36px;
      color: #a0a0a0;
      margin: 20px 0 40px;
    }
    .timeline {
      display: flex;
      gap: 20px;
      justify-content: center;
      margin: 40px 0;
    }
    .segment {
      width: 150px;
      height: 80px;
      background: rgba(59, 130, 246, 0.2);
      border: 2px solid #3b82f6;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .features {
      display: flex;
      gap: 40px;
      justify-content: center;
      margin: 40px 0;
      font-size: 20px;
    }
    .url {
      font-family: 'JetBrains Mono', monospace;
      font-size: 20px;
      color: #60a5fa;
      margin-top: 40px;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="icon">🎬</div>
    <h1 class="title">VIDEO FOUNDRY</h1>
    <p class="subtitle">Scalable AI Video Generation Pipeline</p>

    <div class="timeline">
      <div class="segment">Seg 1</div>
      <div class="segment">Seg 2</div>
      <div class="segment">Seg 3</div>
    </div>

    <div class="features">
      <span>✨ Timeline Editor</span>
      <span>🚀 Intelligent Re-rendering</span>
      <span>🔌 Multi-Model</span>
    </div>

    <div class="url">github.com/QFiSouthaven/Jynco</div>
  </div>
</body>
</html>
```

**To generate image**:
1. Save HTML file
2. Open in Chrome
3. Take screenshot (1200x630)
4. Or use https://www.browserframe.com/

### Option 4: Quick Tools

**Online Generators**:
- https://www.bannerbear.com/ (API available)
- https://www.placeit.net/ (templates)
- https://studio.polotno.com/ (free editor)

**Command Line** (using ImageMagick):
```bash
convert -size 1200x630 \
  gradient:'#1e3a8a'-'#0f172a' \
  -font Arial-Bold \
  -pointsize 72 \
  -fill white \
  -gravity center \
  -annotate +0-100 'VIDEO FOUNDRY' \
  -pointsize 36 \
  -fill '#a0a0a0' \
  -annotate +0-20 'Scalable AI Video Generation Pipeline' \
  -pointsize 20 \
  -fill '#60a5fa' \
  -annotate +0+280 'github.com/QFiSouthaven/Jynco' \
  video-foundry-social-card.png
```

## Content Variations

### Variation 1: Feature Focus
```
VIDEO FOUNDRY

Timeline-Aware AI Video Generation

✨ Multi-Segment Projects
🔄 Intelligent Re-Rendering
🚀 Horizontal Scaling
⚡ Real-Time Progress

github.com/QFiSouthaven/Jynco
```

### Variation 2: Tech Stack
```
VIDEO FOUNDRY

Production-Ready AI Video Pipeline

FastAPI • React • TypeScript • Docker
RabbitMQ • PostgreSQL • Redis • FFMPEG

Runway Gen-3 • Stability AI • Extensible

github.com/QFiSouthaven/Jynco
```

### Variation 3: Use Case
```
VIDEO FOUNDRY

Create Multi-Segment AI Videos

🎬 Social Media Content
📺 Promotional Videos
🎓 Educational Content
🎨 Creative Storytelling

Open Source • Self-Hosted • Production-Ready

github.com/QFiSouthaven/Jynco
```

## Adding to GitHub

1. Go to repository settings
2. Scroll to "Social preview"
3. Click "Upload an image"
4. Upload `video-foundry-social-card.png`
5. Image will appear when sharing on social media

## Social Media Posts

Use these templates when sharing:

### Twitter/X
```
🎬 Introducing Video Foundry v1.0.0

An open-source, timeline-aware AI video generation pipeline.

✨ Visual timeline editor
🔄 Smart re-rendering
🔌 Pluggable AI models
🚀 Production-ready

Built with FastAPI, React, Docker.

Try it: github.com/QFiSouthaven/Jynco

#AI #VideoGeneration #OpenSource #FastAPI #React
```

### LinkedIn
```
Excited to announce Video Foundry v1.0.0! 🎬

After months of development, we're open-sourcing our timeline-aware AI video generation pipeline.

What makes it special:
• Visual timeline editor for multi-segment projects
• Intelligent re-rendering (only regenerate what changed)
• Support for Runway Gen-3, Stability AI, and custom models
• Production-ready with Docker, FastAPI, React
• Horizontal scaling out of the box

Perfect for content creators, marketers, and developers building AI video tools.

Check it out: github.com/QFiSouthaven/Jynco

#ArtificialIntelligence #VideoGeneration #OpenSource #SoftwareEngineering
```

### Reddit (r/MachineLearning, r/programming, r/opensource)
```
[P] Video Foundry v1.0.0 - Open-source AI video generation pipeline with timeline editor

I'm excited to share Video Foundry, a production-ready system for generating AI videos with intelligent segment management.

Key features:
- Timeline editor for multi-segment video projects
- Smart re-rendering (only regenerates changed segments)
- Pluggable AI model architecture (Runway, Stability AI, custom)
- Real-time progress tracking via WebSocket
- Docker-based deployment with horizontal scaling

Tech stack: FastAPI, React, TypeScript, PostgreSQL, RabbitMQ, Redis

The project includes complete documentation, E2E tests, and Docker Compose setup for easy local development.

GitHub: github.com/QFiSouthaven/Jynco

Happy to answer any questions!
```

### Hacker News
```
Show HN: Video Foundry – Open-source AI video generation pipeline

Video Foundry is a timeline-aware system for creating multi-segment AI videos. It features intelligent re-rendering (only regenerate changed segments), support for multiple AI models, and a production-ready architecture with Docker.

The system is built with FastAPI, React, and uses RabbitMQ for distributed task processing. It's designed to handle real production workloads with horizontal scaling.

Looking for feedback on the architecture and use cases!

GitHub: https://github.com/QFiSouthaven/Jynco
```

## Checklist

Before sharing:

- [ ] Social card created (1200x630px)
- [ ] Uploaded to GitHub repository settings
- [ ] Card looks good on preview
- [ ] Text is readable at thumbnail size
- [ ] GitHub URL is correct
- [ ] Brand colors consistent
- [ ] File size under 5MB
- [ ] Tested on Twitter Card Validator
- [ ] Tested on LinkedIn Post Inspector
- [ ] Tested on Facebook Sharing Debugger

## Tools & Resources

**Design Tools**:
- Figma: https://figma.com
- Canva: https://canva.com
- Photopea (free): https://www.photopea.com/

**Preview Tools**:
- Twitter Card Validator: https://cards-dev.twitter.com/validator
- LinkedIn Post Inspector: https://www.linkedin.com/post-inspector/
- Facebook Debugger: https://developers.facebook.com/tools/debug/

**Icon Resources**:
- Heroicons: https://heroicons.com/
- Lucide Icons: https://lucide.dev/
- Phosphor Icons: https://phosphoricons.com/

**Font Resources**:
- Google Fonts: https://fonts.google.com/
- Inter: https://rsms.me/inter/
- JetBrains Mono: https://www.jetbrains.com/lp/mono/

Ready to create your social share card! 🎨
