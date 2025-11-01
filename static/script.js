// ===================================
// UTILITY FUNCTIONS
// ===================================

// Show loading state on button
function setButtonLoading(button, isLoading) {
    if (isLoading) {
        button.disabled = true;
        button.dataset.originalText = button.innerHTML;
        button.innerHTML = '<span class="loading"></span> Processing...';
    } else {
        button.disabled = false;
        button.innerHTML = button.dataset.originalText;
    }
}

// Show result with animation
function showResult(elementId, content, type = 'info') {
    const resultElement = document.getElementById(elementId);
    resultElement.innerHTML = content;
    resultElement.classList.add('show');
    
    // Smooth scroll to result
    setTimeout(() => {
        resultElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}

// Format currency
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value);
}

// Format percentage
function formatPercentage(value) {
    return `${(value * 100).toFixed(2)}%`;
}

// Create badge HTML
function createBadge(text, type) {
    const icons = {
        success: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
        error: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
        warning: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
        info: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>'
    };
    
    return `<div class="result-badge ${type}">${icons[type] || ''}${text}</div>`;
}

// ===================================
// FRAUD DETECTION
// ===================================
document.getElementById("fraud-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const submitButton = e.target.querySelector('button[type="submit"]');
    const formData = Object.fromEntries(new FormData(e.target).entries());

    // Convert numeric fields to float
    const numericFields = [
        "amount", "oldbalanceOrg", "newbalanceOrig", 
        "oldbalanceDest", "newbalanceDest", 
        "balance_diff_orig", "balance_diff_dest", 
        "error_balance_orig", "error_balance_dest"
    ];
    
    numericFields.forEach(field => {
        formData[field] = parseFloat(formData[field]);
    });

    setButtonLoading(submitButton, true);

    try {
        const res = await fetch("/predict_fraud", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(formData)
        });
        
        const data = await res.json();
        
        if (data.error) {
            showResult("fraud-result", `
                ${createBadge('Error', 'error')}
                <h3>Analysis Failed</h3>
                <p>${data.error}</p>
            `, 'error');
        } else {
            const isFraud = data.is_fraud === 'Yes' || data.is_fraud === true || data.is_fraud === 1;
            const probability = parseFloat(data.fraud_probability);
            const badgeType = isFraud ? 'error' : 'success';
            const badgeText = isFraud ? 'Fraud Detected' : 'Transaction Safe';
            
            showResult("fraud-result", `
                ${createBadge(badgeText, badgeType)}
                <h3>Fraud Analysis Results</h3>
                <div style="margin-top: 1rem;">
                    <p><strong>Transaction Type:</strong> ${formData.type}</p>
                    <p><strong>Amount:</strong> ${formatCurrency(formData.amount)}</p>
                    <p><strong>Fraud Status:</strong> <span style="color: ${isFraud ? 'var(--error-color)' : 'var(--success-color)'}">${isFraud ? 'FRAUDULENT' : 'LEGITIMATE'}</span></p>
                    <p><strong>Fraud Probability:</strong> ${formatPercentage(probability)}</p>
                </div>
                ${isFraud ? '<p style="margin-top: 1rem; padding: 0.75rem; background: rgba(239, 68, 68, 0.1); border-radius: 0.5rem; border-left: 3px solid var(--error-color);"><strong>⚠️ Warning:</strong> This transaction shows high risk indicators. Please review carefully before processing.</p>' : ''}
            `, badgeType);
        }
    } catch (err) {
        showResult("fraud-result", `
            ${createBadge('Connection Error', 'error')}
            <h3>Request Failed</h3>
            <p>Unable to connect to the server. Please check your connection and try again.</p>
            <p style="color: var(--text-tertiary); font-size: 0.875rem; margin-top: 0.5rem;">${err.message}</p>
        `, 'error');
    } finally {
        setButtonLoading(submitButton, false);
    }
});

// ===================================
// BUDGET PREDICTION
// ===================================
document.getElementById("budget-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const submitButton = e.target.querySelector('button[type="submit"]');
    const formData = Object.fromEntries(new FormData(e.target).entries());

    // Convert numeric fields to float
    const numericFields = ["amount", "oldbalanceOrg", "newbalanceOrig", "balance_diff_orig"];
    numericFields.forEach(field => {
        formData[field] = parseFloat(formData[field]);
    });

    setButtonLoading(submitButton, true);

    try {
        const res = await fetch("/predict_budget", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(formData)
        });
        
        const data = await res.json();
        
        if (data.error) {
            showResult("budget-result", `
                ${createBadge('Error', 'error')}
                <h3>Prediction Failed</h3>
                <p>${data.error}</p>
            `, 'error');
        } else {
            const spendingChange = parseFloat(data.predicted_spending_change);
            const isIncrease = spendingChange > 0;
            const badgeType = isIncrease ? 'warning' : 'success';
            const badgeText = isIncrease ? 'Spending Increase' : 'Spending Decrease';
            
            showResult("budget-result", `
                ${createBadge(badgeText, badgeType)}
                <h3>Budget Forecast</h3>
                <div style="margin-top: 1rem;">
                    <p><strong>Transaction Amount:</strong> ${formatCurrency(formData.amount)}</p>
                    <p><strong>Current Balance:</strong> ${formatCurrency(formData.newbalanceOrig)}</p>
                    <p><strong>Predicted Spending Change:</strong> <span style="color: ${isIncrease ? 'var(--warning-color)' : 'var(--success-color)'}; font-size: 1.25rem; font-weight: 700;">${formatCurrency(Math.abs(spendingChange))}</span></p>
                    <p><strong>Direction:</strong> ${isIncrease ? '📈 Upward trend' : '📉 Downward trend'}</p>
                </div>
                <p style="margin-top: 1rem; padding: 0.75rem; background: rgba(99, 102, 241, 0.1); border-radius: 0.5rem; border-left: 3px solid var(--info-color);">
                    <strong>💡 Insight:</strong> ${isIncrease 
                        ? 'Your spending is projected to increase. Consider reviewing your budget allocation.' 
                        : 'Your spending is projected to decrease. You\'re on track with your financial goals!'}
                </p>
            `, badgeType);
        }
    } catch (err) {
        showResult("budget-result", `
            ${createBadge('Connection Error', 'error')}
            <h3>Request Failed</h3>
            <p>Unable to connect to the server. Please check your connection and try again.</p>
            <p style="color: var(--text-tertiary); font-size: 0.875rem; margin-top: 0.5rem;">${err.message}</p>
        `, 'error');
    } finally {
        setButtonLoading(submitButton, false);
    }
});

// ===================================
// INVESTMENT SUGGESTION
// ===================================
// ===================================
// INVESTMENT SUGGESTION (Updated for LSTM)
// ===================================
document.getElementById("investment-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const submitButton = e.target.querySelector('button[type="submit"]');
    const formData = Object.fromEntries(new FormData(e.target).entries());

    // Convert all investment fields to float
    const numericFields = ["Close_BTC", "Close_ETH", "Close_BNB", "Close_BTC_SMA7", "Close_BTC_SMA30"];
    numericFields.forEach(field => {
        formData[field] = parseFloat(formData[field]);
    });

    setButtonLoading(submitButton, true);

    try {
        const res = await fetch("/suggest_investment", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(formData)
        });
        
        const data = await res.json();
        
        if (data.error) {
            showResult("investment-result", `
                ${createBadge('Error', 'error')}
                <h3>Analysis Failed</h3>
                <p>${data.error}</p>
            `, 'error');
        } else {
            // Display predicted next-step values
            const predictedFeatures = data.predicted_features;
            const growthScore = parseFloat(data.growth_score);
            const recommendation = data.recommendation;

            const featureCards = Object.keys(predictedFeatures).map(key => `
                <div style="padding: 0.75rem; background: var(--bg-tertiary); border-radius: 0.5rem;">
                    <p style="font-size: 0.75rem; color: var(--text-tertiary); margin-bottom: 0.25rem;">${key}</p>
                    <p style="font-size: 1.125rem; font-weight: 700;">${formatCurrency(predictedFeatures[key])}</p>
                </div>
            `).join('');

            showResult("investment-result", `
                ${createBadge('Analysis Complete', 'success')}
                <h3>Investment Forecast (Next Step)</h3>
                <div style="margin-top: 1rem;">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 0.75rem; margin-bottom: 1rem;">
                        ${featureCards}
                    </div>
                    
                    <div style="padding: 1rem; background: rgba(16, 185, 129, 0.1); border-radius: 0.5rem; border-left: 3px solid var(--success-color);">
                        <p><strong>💼 Recommendation:</strong></p>
                        <p style="margin-top: 0.5rem;">${recommendation}</p>
                        <p style="margin-top: 0.5rem; font-size: 0.875rem; color: var(--text-tertiary);">
                            Growth Score: ${growthScore.toFixed(4)}
                        </p>
                    </div>
                </div>
            `, 'success');
        }
    } catch (err) {
        showResult("investment-result", `
            ${createBadge('Connection Error', 'error')}
            <h3>Request Failed</h3>
            <p>Unable to connect to the server. Please check your connection and try again.</p>
            <p style="color: var(--text-tertiary); font-size: 0.875rem; margin-top: 0.5rem;">${err.message}</p>
        `, 'error');
    } finally {
        setButtonLoading(submitButton, false);
    }
});


// ===================================
// CRYPTO TICKER
// ===================================
document.getElementById("load-crypto").addEventListener("click", async (e) => {
    const button = e.target;
    setButtonLoading(button, true);

    try {
        const res = await fetch("/crypto_ticker");
        const data = await res.json();
        
        if (data.error) {
            showResult("crypto-result", `
                ${createBadge('Error', 'error')}
                <h3>Unable to Load Data</h3>
                <p>${data.error}</p>
            `, 'error');
            return;
        }

        // Format the crypto data in a beautiful grid
        const cryptoData = [
            { name: 'Bitcoin', symbol: 'BTC', price: data.BTC_Close, volume: data.BTC_Volume, color: '#F7931A' },
            { name: 'Ethereum', symbol: 'ETH', price: data.ETH_Close, volume: data.ETH_Volume, color: '#627EEA' },
            { name: 'Tether', symbol: 'USDT', price: data.USDT_Close, volume: data.USDT_Volume, color: '#26A17B' },
            { name: 'BNB', symbol: 'BNB', price: data.BNB_Close, volume: data.BNB_Volume, color: '#F3BA2F' }
        ];

        const cryptoCards = cryptoData.map(crypto => `
            <div class="crypto-item" style="border-left: 3px solid ${crypto.color};">
                <div class="crypto-name">${crypto.name} (${crypto.symbol})</div>
                <div class="crypto-price">${formatCurrency(crypto.price)}</div>
                <div style="font-size: 0.75rem; color: var(--text-tertiary); margin-top: 0.5rem;">
                    Volume: ${new Intl.NumberFormat('en-US', { notation: 'compact', compactDisplay: 'short' }).format(crypto.volume)}
                </div>
            </div>
        `).join('');

        showResult("crypto-result", `
            ${createBadge('Live Data', 'success')}
            <h3>Cryptocurrency Market Data</h3>
            <p style="color: var(--text-tertiary); font-size: 0.875rem; margin-bottom: 1rem;">
                📅 <strong>Last Updated:</strong> ${data.Date || new Date().toLocaleDateString()}
            </p>
            <div class="crypto-grid">
                ${cryptoCards}
            </div>
            <p style="margin-top: 1rem; padding: 0.75rem; background: rgba(99, 102, 241, 0.1); border-radius: 0.5rem; font-size: 0.875rem;">
                <strong>ℹ️ Note:</strong> Prices are updated in real-time. Use this data for informational purposes only.
            </p>
        `, 'success');
    } catch (err) {
        showResult("crypto-result", `
            ${createBadge('Connection Error', 'error')}
            <h3>Request Failed</h3>
            <p>Unable to fetch cryptocurrency data. Please check your connection and try again.</p>
            <p style="color: var(--text-tertiary); font-size: 0.875rem; margin-top: 0.5rem;">${err.message}</p>
        `, 'error');
    } finally {
        setButtonLoading(button, false);
    }
});

// ===================================
// INITIALIZATION
// ===================================
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 FinAI Advisor Dashboard Initialized');
    
    // Add smooth animations to cards on page load
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
});