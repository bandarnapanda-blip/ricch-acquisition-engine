import React, { useState } from 'react';
import { motion } from 'motion/react';
import { Sparkles, Image as ImageIcon, Loader2, Download } from 'lucide-react';
import { GoogleGenAI } from '@google/genai';

export function AiImageGenerator() {
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedImage, setGeneratedImage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!prompt.trim()) return;
    
    setIsGenerating(true);
    setError(null);
    
    try {
      // Initialize Gemini API
      const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
      
      const response = await ai.models.generateContent({
        model: 'gemini-3.1-flash-image-preview',
        contents: {
          parts: [
            {
              text: prompt,
            },
          ],
        },
        config: {
          imageConfig: {
            aspectRatio: "16:9",
            imageSize: "1K"
          }
        },
      });

      let foundImage = false;
      for (const part of response.candidates?.[0]?.content?.parts || []) {
        if (part.inlineData) {
          const base64EncodeString = part.inlineData.data;
          setGeneratedImage(`data:image/png;base64,${base64EncodeString}`);
          foundImage = true;
          break;
        }
      }

      if (!foundImage) {
        throw new Error("No image was generated. Please try a different prompt.");
      }
    } catch (err: any) {
      console.error("Image generation error:", err);
      setError(err.message || "Failed to generate image. Please try again.");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight text-apple-base">Showcase Generator</h1>
          <p className="text-sm text-apple-muted mt-1">Generate high-converting ad creatives using Nano Banana 2.</p>
        </div>
        <Sparkles className="text-primary" size={28} />
      </div>

      <div className="liquid-glass rounded-3xl p-8 mb-8">
        <div className="flex flex-col gap-4">
          <label className="text-sm font-medium text-apple-base">Creative Prompt</label>
          <div className="relative">
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe the ad creative you want to generate... (e.g., 'A modern SaaS dashboard glowing in neon blue, high quality, 4k')"
              className="w-full liquid-glass rounded-2xl p-4 text-sm text-apple-base placeholder:text-apple-muted focus:outline-none focus:ring-2 focus:ring-white/50 transition-all min-h-[120px] resize-none"
            />
          </div>
          <div className="flex justify-end">
            <button
              onClick={handleGenerate}
              disabled={isGenerating || !prompt.trim()}
              className="bg-apple-base text-bg dark:bg-white dark:text-black py-3 px-6 rounded-xl text-sm font-medium hover:opacity-90 transition-all shadow-lg flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isGenerating ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles size={16} />
                  Generate Creative
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {error && (
        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-danger/10 border border-danger/20 text-danger p-4 rounded-2xl mb-8 text-sm"
        >
          {error}
        </motion.div>
      )}

      {generatedImage ? (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="liquid-glass rounded-3xl overflow-hidden relative group"
        >
          <img 
            src={generatedImage} 
            alt="Generated Creative" 
            className="w-full h-auto object-cover aspect-video"
          />
          <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center backdrop-blur-sm">
            <a 
              href={generatedImage} 
              download="creative.png"
              className="bg-white text-black py-3 px-6 rounded-xl text-sm font-medium hover:scale-105 transition-all flex items-center gap-2"
            >
              <Download size={16} />
              Download Asset
            </a>
          </div>
        </motion.div>
      ) : (
        <div className="liquid-glass rounded-3xl p-12 flex flex-col items-center justify-center text-center border-dashed border-2 border-white/10 aspect-video">
          <ImageIcon size={48} className="text-apple-muted/30 mb-4" />
          <p className="text-apple-muted font-medium">Your generated creative will appear here</p>
        </div>
      )}
    </div>
  );
}
