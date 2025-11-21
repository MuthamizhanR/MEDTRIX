import os
import re

TARGET_DIR = "extracted_tests"

# --- 1. THE JAVASCRIPT LISTENER (Inserted into the <head> of every quiz) ---
LISTENER_SCRIPT = """
<script>
    // --- GEMINI AUTO-CAPTURE LISTENER ---
    // This function runs immediately after the quiz determines an answer is INCORRECT.
    function captureMistake(questionIndex, questionsData) {
        try {
            const item = questionsData[questionIndex];
            // Use the question text as a unique, stable identifier
            const uniqueId = 'srs_quiz_' + btoa(item.text.substring(0, 50)).replace(/=/g, ''); 

            // 1. Clean and simplify the explanation for storage
            let explanationText = item.explanation || item.correct_answer || "No explanation provided.";
            
            // Strip complex HTML (images, lists) and boilerplate text
            explanationText = explanationText.replace(/<img[^>]*>/g, "[IMAGE]").trim(); // Replace images with placeholder
            explanationText = explanationText.replace(/<p><strong>Ans\. [A-Z]\).*/i, "").trim(); // Remove the repeated Answer line
            explanationText = explanationText.replace(/<p><strong>Educational Objective:<\/strong>.*?<\/p>/gs, "").trim(); // Remove EO block
            explanationText = explanationText.replace(/@dams_new_robot/g, "");
            explanationText = explanationText.replace(/<\/?[^>]+(>|$)/g, " ").trim(); // Final strip of remaining tags

            // 2. Prepare card data
            const cardData = {
                text: item.text,
                answer: item.correct_answer,
                explanation: explanationText.substring(0, 500), // Keep explanations short
                nextReview: 0, // Due immediately
                reviews: 0,
                source: document.title.split('-')[0].trim() || 'Quiz'
            };

            // 3. Save to Local Storage (SRS Bank)
            localStorage.setItem(uniqueId, JSON.stringify(cardData));
            
            console.log(`🧠 Captured Mistake #${questionIndex + 1} from ${document.title}`);

        } catch (e) {
            console.error("SRS Capture Failed:", e);
        }
    }
    // --- END GEMINI AUTO-CAPTURE LISTENER ---
</script>
"""

# --- 2. THE CORE INJECTION CODE ---
# This is the line that will be inserted directly into the quiz's check logic.
# It uses the variable names found in your extracted files (current_question_index, questions_data)
CAPTURE_CALL = r"""
        if (selectedOption.correct) {
            // Original code follows here...
        } else {
            document.getElementById('explanation').innerHTML = question.explanation;
            document.getElementById('explanation').style.display = 'block';
            captureMistake(current_question_index, questions_data); // <<< GEMINI INJECTION HERE
        }"""

# Pattern to find the *exact* spot inside the internal quiz logic
# We look for the 'else' block where the explanation is shown (meaning the answer was wrong)
# The pattern must be precise to avoid breaking the file.
# It looks for the start of the 'else' block immediately following the correct/incorrect decision logic.
INJECTION_PATTERN = r"""if \(selectedOption\.correct\) \{\n\s*// Original code follows here\.\.\.\n\s*\} else \{\n\s*document\.getElementById\('explanation'\)\.innerHTML = question\.explanation;\n\s*document\.getElementById\('explanation'\)\.style\.display = 'block';\n"""

def inject_listener():
    print(f"--- INJECTING AUTO-CAPTURE LISTENER into {TARGET_DIR} ---")
    
    if not os.path.exists(TARGET_DIR):
        print(f"❌ Error: Directory {TARGET_DIR} not found. Please run extraction first.")
        return 0

    injected_count = 0
    for filename in os.listdir(TARGET_DIR):
        if not filename.endswith('.html'):
            continue
            
        filepath = os.path.join(TARGET_DIR, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # 1. Skip if already injected
            if 'GEMINI AUTO-CAPTURE LISTENER' in content:
                continue

            # 2. Inject the base script tag into the <head>
            if '</head>' in content:
                content = content.replace('</head>', LISTENER_SCRIPT + '\n</head>')
            
            # 3. Find the injection spot and insert the capture call
            # We look for the start of the 'else' block and insert the capture function right after showing the explanation.
            
            # NOTE: We need a slight modification to the CAPTURE_CALL to match the original structure.
            
            # The original structure seems to be:
            # if (selectedOption.correct) { ... } else { show explanation; }
            # Let's adjust the pattern to insert the capture call after the explanation is shown.

            # Find the line that shows the explanation:
            EXPLANATION_LINE = r"document.getElementById('explanation').innerHTML = question.explanation;\n\s*document.getElementById('explanation').style.display = 'block';"
            
            # The insertion code (calling the capture function)
            INSERTION_CALL = r"\n            document.getElementById('explanation').innerHTML = question.explanation;\n            document.getElementById('explanation').style.display = 'block';\n            captureMistake(current_question_index, questions_data);"
            
            # The regex substitution
            if re.search(EXPLANATION_LINE, content):
                # Replace the explanation display line with the same line PLUS the capture call
                content = re.sub(EXPLANATION_LINE, INSERTION_CALL.strip(), content)
                injected_count += 1
            else:
                # Fallback: Just save the file with the base listener if the internal logic is too complex/different
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                continue # Skip incrementing injected_count if core logic wasn't modified

            # Save the modified file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
        except Exception as e:
            print(f"❌ Failed to process {filepath}: {e}")
            
    print(f"🎉 Successfully modified logic in {injected_count} test files.")
    
    # Final Instruction to the User
    print("\n\n#####################################################################")
    print("## FINAL STEP REQUIRED: MANUAL TEST ##")
    print("#####################################################################")
    print("1. Open any quiz (e.g., CEREB Anatomy).")
    print("2. Answer a question INCORRECTLY.")
    print("3. Check the browser console (F12) for the message: '🧠 Captured Mistake #X'.")
    print("4. Check the 'Smart Revision' page to see the flashcard.")
    print("If it does not work, the internal JavaScript structure has changed, and we will need to analyze the main JS function.")
    print("#####################################################################")
    
    return injected_count

if __name__ == "__main__":
    inject_listener()