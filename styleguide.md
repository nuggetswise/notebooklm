

## Comprehensive Style Guide Prompt for Chat App Frontend

Here's a detailed prompt you can use:

---

**Chat App Frontend Style Guide & Implementation Requirements**

Please implement a chat application frontend following these exact specifications to maintain consistency with our existing design system:

### **Technology Stack**
- **Framework**: Next.js 15+ with TypeScript
- **Styling**: Tailwind CSS with CSS variables for theming
- **UI Components**: shadcn/ui component library
- **Icons**: Lucide React icons
- **State Management**: React hooks (useState, useEffect, useCallback)
- **Forms**: React Hook Form with Zod validation

### **Core Dependencies**
```json
{
  "dependencies": {
    "next": "15.2.4",
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "typescript": "5.8.3",
    "tailwindcss": "^3.4.17",
    "tailwindcss-animate": "^1.0.7",
    "class-variance-authority": "^0.7.1",
    "clsx": "^2.1.1",
    "tailwind-merge": "^2.5.5",
    "lucide-react": "^0.454.0",
    "@radix-ui/react-*": "latest",
    "react-markdown": "^9.0.1"
  }
}
```

### **Design System Configuration**

**1. Tailwind Configuration (`tailwind.config.ts`)**
```typescript
import type { Config } from "tailwindcss"

const config = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
} satisfies Config

export default config
```

**2. Global CSS Variables (`app/globals.css`)**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 240 10% 3.9%;
    --card: 0 0% 100%;
    --card-foreground: 240 10% 3.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 240 10% 3.9%;
    --primary: 250 100% 69%;
    --primary-foreground: 0 0% 98%;
    --secondary: 240 4.8% 95.9%;
    --secondary-foreground: 240 5.9% 10%;
    --muted: 240 4.8% 95.9%;
    --muted-foreground: 240 3.8% 46.1%;
    --accent: 240 4.8% 95.9%;
    --accent-foreground: 240 5.9% 10%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 0 0% 98%;
    --border: 240 5.9% 90%;
    --input: 240 5.9% 90%;
    --ring: 250 100% 69%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 240 10% 3.9%;
    --foreground: 0 0% 98%;
    --card: 240 10% 3.9%;
    --card-foreground: 0 0% 98%;
    --popover: 240 10% 3.9%;
    --popover-foreground: 0 0% 98%;
    --primary: 250 100% 69%;
    --primary-foreground: 0 0% 98%;
    --secondary: 240 3.7% 15.9%;
    --secondary-foreground: 0 0% 98%;
    --muted: 240 3.7% 15.9%;
    --muted-foreground: 240 5% 64.9%;
    --accent: 240 3.7% 15.9%;
    --accent-foreground: 0 0% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 0 0% 98%;
    --border: 240 3.7% 15.9%;
    --input: 240 3.7% 15.9%;
    --ring: 250 100% 69%;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

### **Core UI Components Structure**

**1. Button Component Pattern**
```typescript
const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)
```

**2. Card Component Pattern**
```typescript
const Card = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn("rounded-lg border bg-card text-card-foreground shadow-sm", className)}
      {...props}
    />
  )
)
```

### **Chat Interface Layout Structure**

**1. Main Container Layout**
```typescript
<main className="h-[calc(100vh-4rem)] p-2 sm:p-4">
  <div className="h-full flex flex-col">
    <Card className="h-full flex flex-col">
      {/* Header */}
      <CardHeader className="flex flex-row items-center justify-between pb-2 sm:pb-4 px-3 sm:px-6">
        {/* Header content */}
      </CardHeader>
      
      {/* Chat Content */}
      <div className="flex-1 overflow-hidden">
        {/* Messages area */}
      </div>
      
      {/* Input Footer */}
      <CardFooter className="pt-2 sm:pt-4 flex flex-col gap-2 sm:gap-3 px-3 sm:px-6 pb-3 sm:pb-6">
        {/* Input form */}
      </CardFooter>
    </Card>
  </div>
</main>
```

**2. Message Display Pattern**
```typescript
<div className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}>
  <div className={`max-w-[80%] rounded-lg p-3 ${
    message.sender === "user" 
      ? "bg-primary text-primary-foreground" 
      : "bg-muted text-muted-foreground"
  }`}>
    <ReactMarkdown>{message.text}</ReactMarkdown>
  </div>
</div>
```

**3. Input Form Pattern**
```typescript
<form className="flex w-full space-x-2" onSubmit={handleSubmit}>
  <Input
    placeholder="Type your message..."
    value={inputValue}
    onChange={(e) => setInputValue(e.target.value)}
    className="flex-1"
  />
  <Button 
    type="submit" 
    size="icon" 
    className="transition-all duration-150 hover:bg-primary/90 hover:shadow-sm"
    disabled={!inputValue.trim() || isTyping}
  >
    <Send className="h-4 w-4" />
  </Button>
</form>
```

### **Key Design Principles**

1. **Responsive Design**: Use `sm:` prefixes for mobile-first responsive design
2. **Spacing**: Consistent padding with `p-2 sm:p-4` pattern
3. **Typography**: Use `text-sm` for most text, `text-xs` for secondary text
4. **Colors**: Use CSS variables for all colors to support dark/light themes
5. **Transitions**: Use `transition-all duration-150` for smooth interactions
6. **Loading States**: Use `animate-spin` with primary color borders
7. **Hover Effects**: Subtle hover states with opacity changes (`hover:bg-primary/90`)

### **Component Organization**
```
components/
├── ui/           # shadcn/ui components
├── chat-house.tsx
├── chat-interface.tsx
├── message-bubble.tsx
├── input-form.tsx
└── loading-spinner.tsx
```

### **State Management Pattern**
```typescript
const [messages, setMessages] = useState<ChatMessage[]>([])
const [inputValue, setInputValue] = useState("")
const [isTyping, setIsTyping] = useState(false)
const messagesEndRef = useRef<HTMLDivElement>(null)

// Auto-scroll to bottom
useEffect(() => {
  messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
}, [messages])
```

### **Required Features**
- Real-time message updates
- Auto-scroll to latest message
- Loading states for message sending
- Responsive design for mobile/desktop
- Dark/light theme support
- Message timestamps
- User avatar support
- Typing indicators
- Error handling with toast notifications

### **Accessibility Requirements**
- Proper ARIA labels
- Keyboard navigation support
- Focus management
- Screen reader compatibility
- High contrast mode support

This style guide ensures your new chat app will have the exact same visual design, component structure, and user experience as the existing application. Follow these specifications precisely to maintain design consistency across both applications.