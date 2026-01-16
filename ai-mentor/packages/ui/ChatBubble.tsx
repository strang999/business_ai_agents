import React from "react";
import { View, Text, ViewProps } from "react-native";
import { styled } from "nativewind";

// NativeWind styled components
const StyledView = styled(View);
const StyledText = styled(Text);

interface ChatBubbleProps extends ViewProps {
  message: string;
  isUser: boolean;
  timestamp?: string;
  isCrisis?: boolean;
}

/**
 * Universal Chat Bubble Component
 * Works on Native (iOS/Android) and Web (Next.js) via NativeWind.
 * 
 * Design: "Glassmorphism" effect for AI, Solid color for User.
 */
export const ChatBubble: React.FC<ChatBubbleProps> = ({ 
  message, 
  isUser, 
  timestamp,
  isCrisis,
  ...props 
}) => {
  return (
    <StyledView
      className={`
        max-w-[80%] 
        p-4 
        rounded-2xl 
        my-2 
        ${isUser ? "self-end bg-blue-600 rounded-br-none" : "self-start bg-white/10 border border-white/20 backdrop-blur-md rounded-bl-none"}
        ${isCrisis ? "border-red-500 bg-red-900/20" : ""}
      `}
      {...props}
    >
      <StyledText 
        className={`
          text-base 
          leading-6
          ${isUser ? "text-white" : "text-gray-100"}
          ${isCrisis ? "text-red-200 font-bold" : ""}
        `}
      >
        {message}
      </StyledText>
      
      {timestamp && (
        <StyledText className="text-xs text-white/40 mt-1 self-end">
          {timestamp}
        </StyledText>
      )}
    </StyledView>
  );
};
