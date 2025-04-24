document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const userMessageInput = document.getElementById('user-message');
    const sendRequestButton = document.getElementById('send-request');
    const domainSelect = document.getElementById('domain-select');
    const domainValue = document.getElementById('domain-value');
    const messagePlaceholder = document.getElementById('message-placeholder');
    const responseJson = document.getElementById('response-json');
    const responseContent = document.getElementById('response-content');
    const responseSpinner = document.getElementById('response-spinner');
    
    // Initialize with placeholder text
    if (userMessageInput) {
        userMessageInput.addEventListener('input', function() {
            if (messagePlaceholder) {
                messagePlaceholder.textContent = this.value || 'Enter your mechanical engineering question here...';
            }
        });
    }
    
    // Update domain value in JSON preview
    if (domainSelect) {
        domainSelect.addEventListener('change', function() {
            if (domainValue) {
                domainValue.textContent = this.value;
            }
        });
    }
    
    // Handle form submission
    if (sendRequestButton) {
        sendRequestButton.addEventListener('click', function() {
            const message = userMessageInput.value.trim();
            const domain = domainSelect.value;
            
            if (!message) {
                alert('Please enter a question.');
                return;
            }
            
            // Show loading spinner
            responseSpinner.style.display = 'block';
            
            // Clear previous response
            responseJson.textContent = '// Loading...';
            responseContent.innerHTML = '<div class="placeholder-text">Loading response...</div>';
            
            // Prepare request
            const requestData = {
                message: message,
                domain: domain
            };
            
            // Send API request
            fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                // Format JSON for display
                const formattedJson = JSON.stringify(data, null, 2);
                responseJson.textContent = formattedJson;
                
                // Format the response content with markdown-like formatting
                let formattedResponse = data.response || 'No response received';
                
                // Basic formatting (convert line breaks to <br>)
                formattedResponse = formattedResponse.replace(/\n\n/g, '</p><p>');
                formattedResponse = formattedResponse.replace(/\n/g, '<br>');
                
                // Format lists
                formattedResponse = formattedResponse.replace(/- (.*?)(<br>|<\/p>)/g, '<li>$1</li>$2');
                formattedResponse = formattedResponse.replace(/<li>(.*?)<\/li><br><li>/g, '<li>$1</li><li>');
                formattedResponse = formattedResponse.replace(/<p><li>/g, '<p><ul><li>');
                formattedResponse = formattedResponse.replace(/<\/li><\/p>/g, '</li></ul></p>');
                
                // Wrap in paragraphs if not already
                if (!formattedResponse.startsWith('<p>')) {
                    formattedResponse = '<p>' + formattedResponse;
                }
                if (!formattedResponse.endsWith('</p>')) {
                    formattedResponse += '</p>';
                }
                
                // Display formatted response
                responseContent.innerHTML = formattedResponse;
            })
            .catch(error => {
                console.error('Error:', error);
                responseJson.textContent = `// Error: ${error.message}`;
                responseContent.innerHTML = `<p class="error-message">Error: ${error.message}</p>`;
            })
            .finally(() => {
                // Hide loading spinner
                responseSpinner.style.display = 'none';
            });
        });
    }
    
    // Add ability to press Enter to send message
    if (userMessageInput) {
        userMessageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendRequestButton.click();
            }
        });
    }
});
