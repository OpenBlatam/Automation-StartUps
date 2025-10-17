// Generador de 1000 Campañas de Marketing con IA
const fs = require('fs');

class AICampaignGenerator {
    constructor() {
        this.categories = [
            "Personalización con IA",
            "Análisis Predictivo", 
            "Chatbots y Asistentes Virtuales",
            "Generación de Contenido",
            "Optimización de Conversión",
            "Segmentación Avanzada",
            "Automatización de Marketing",
            "Análisis de Sentimientos",
            "Recomendaciones Inteligentes",
            "Marketing Visual con IA"
        ];
        
        this.channels = [
            "Redes Sociales", "Email Marketing", "SEM/PPC", "Display Advertising",
            "Content Marketing", "Influencer Marketing", "Video Marketing",
            "Mobile Marketing", "E-commerce", "Marketing Automation"
        ];
        
        this.technologies = [
            "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
            "Predictive Analytics", "Neural Networks", "Reinforcement Learning",
            "Generative AI", "Sentiment Analysis", "Recommendation Engines"
        ];
        
        this.objectives = [
            "Aumentar conversiones", "Mejorar engagement", "Generar leads",
            "Aumentar ventas", "Mejorar retención", "Optimizar ROI",
            "Expandir alcance", "Mejorar experiencia de usuario",
            "Reducir costos", "Aumentar brand awareness"
        ];
        
        this.verticals = [
            "E-commerce", "Fintech", "Healthcare", "Education", "Real Estate",
            "Travel & Tourism", "Food & Beverage", "Fashion", "Technology",
            "Automotive", "Entertainment", "Fitness & Wellness"
        ];
        
        this.prefixes = [
            "Smart", "AI-Powered", "Intelligent", "Predictive", "Automated",
            "Dynamic", "Adaptive", "Cognitive", "Neural", "Deep"
        ];
        
        this.actions = [
            "Boost", "Enhance", "Maximize", "Optimize", "Transform",
            "Revolutionize", "Accelerate", "Amplify", "Streamline", "Elevate"
        ];
        
        this.suffixes = [
            "Campaign", "Strategy", "Initiative", "Program", "Solution",
            "Experience", "Journey", "Optimization", "Engagement", "Conversion"
        ];
    }
    
    randomChoice(array) {
        return array[Math.floor(Math.random() * array.length)];
    }
    
    randomFloat(min, max) {
        return Math.random() * (max - min) + min;
    }
    
    randomInt(min, max) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }
    
    generateCampaignName() {
        const prefix = this.randomChoice(this.prefixes);
        const action = this.randomChoice(this.actions);
        const suffix = this.randomChoice(this.suffixes);
        return `${prefix} ${action} ${suffix}`;
    }
    
    generateDescription(category, tech, channel) {
        const descriptions = {
            "Personalización con IA": [
                `Implementa algoritmos de ${tech} para personalizar experiencias únicas en ${channel}, adaptando contenido, ofertas y mensajes en tiempo real según el comportamiento y preferencias de cada usuario.`,
                `Utiliza ${tech} para crear experiencias hiper-personalizadas en ${channel} que aumentan la relevancia y engagement del contenido para cada segmento de audiencia.`,
                `Desarrolla un sistema de personalización inteligente con ${tech} que analiza patrones de comportamiento en ${channel} para ofrecer recomendaciones precisas y contenido adaptativo.`
            ],
            "Análisis Predictivo": [
                `Aplica ${tech} para predecir tendencias de mercado y comportamiento del consumidor en ${channel}, permitiendo decisiones estratégicas basadas en datos.`,
                `Implementa modelos predictivos con ${tech} que anticipan necesidades del cliente en ${channel}, optimizando el timing y contenido de las campañas.`,
                `Utiliza ${tech} para predecir el valor de vida del cliente (LTV) y optimizar estrategias de retención en ${channel}.`
            ],
            "Chatbots y Asistentes Virtuales": [
                `Desarrolla chatbots inteligentes con ${tech} para ${channel} que proporcionan soporte 24/7 y guían a los usuarios a través del embudo de conversión.`,
                `Implementa asistentes virtuales avanzados con ${tech} que personalizan la experiencia de atención al cliente en ${channel}.`,
                `Crea un ecosistema de chatbots especializados con ${tech} para diferentes etapas del customer journey en ${channel}.`
            ],
            "Generación de Contenido": [
                `Utiliza ${tech} para generar automáticamente contenido personalizado y relevante para ${channel}, incluyendo textos, imágenes y videos.`,
                `Implementa herramientas de generación de contenido con ${tech} que crean material de marketing adaptativo para ${channel}.`,
                `Desarrolla un sistema de creación de contenido inteligente con ${tech} que optimiza automáticamente el copy para diferentes audiencias en ${channel}.`
            ],
            "Optimización de Conversión": [
                `Aplica ${tech} para optimizar continuamente la tasa de conversión en ${channel} mediante testing automático y ajustes en tiempo real.`,
                `Implementa algoritmos de ${tech} que identifican y corrigen puntos de fricción en el embudo de conversión de ${channel}.`,
                `Utiliza ${tech} para crear experiencias de conversión personalizadas que maximizan el ROI en ${channel}.`
            ]
        };
        
        const baseDescriptions = descriptions[category] || [
            `Implementa una estrategia innovadora de ${tech} en ${channel} para optimizar resultados mediante análisis avanzado de datos y automatización inteligente.`,
            `Desarrolla una campaña de ${tech} que transforma ${channel} a través de insights predictivos y personalización dinámica.`,
            `Crea una solución de marketing inteligente con ${tech} en ${channel} que optimiza automáticamente el rendimiento.`
        ];
        
        return this.randomChoice(baseDescriptions);
    }
    
    generateMetrics() {
        return {
            conversion_rate: parseFloat(this.randomFloat(2.5, 15.0).toFixed(2)),
            click_through_rate: parseFloat(this.randomFloat(1.8, 8.5).toFixed(2)),
            engagement_rate: parseFloat(this.randomFloat(3.2, 12.8).toFixed(2)),
            cost_per_acquisition: parseFloat(this.randomFloat(15, 85).toFixed(2)),
            return_on_ad_spend: parseFloat(this.randomFloat(3.2, 8.7).toFixed(2)),
            customer_lifetime_value: parseFloat(this.randomFloat(120, 850).toFixed(2)),
            email_open_rate: parseFloat(this.randomFloat(18, 35).toFixed(2)),
            social_media_reach: this.randomInt(50000, 500000),
            website_traffic_increase: parseFloat(this.randomFloat(25, 180).toFixed(2)),
            lead_generation_increase: parseFloat(this.randomFloat(40, 200).toFixed(2))
        };
    }
    
    generateBudget() {
        const budgetTiers = [
            {min: 1000, max: 5000, tier: "Básico"},
            {min: 5000, max: 15000, tier: "Intermedio"},
            {min: 15000, max: 50000, tier: "Avanzado"},
            {min: 50000, max: 150000, tier: "Enterprise"}
        ];
        
        const tier = this.randomChoice(budgetTiers);
        const budget = this.randomInt(tier.min, tier.max);
        
        return {
            amount: budget,
            tier: tier.tier,
            currency: "USD"
        };
    }
    
    generateTimeline() {
        const startDate = new Date();
        startDate.setDate(startDate.getDate() + this.randomInt(1, 30));
        
        const durationWeeks = this.randomInt(4, 16);
        const endDate = new Date(startDate);
        endDate.setDate(endDate.getDate() + (durationWeeks * 7));
        
        return {
            start_date: startDate.toISOString().split('T')[0],
            end_date: endDate.toISOString().split('T')[0],
            duration_weeks: durationWeeks
        };
    }
    
    generateSingleCampaign(id) {
        const category = this.randomChoice(this.categories);
        const tech = this.randomChoice(this.technologies);
        const channel = this.randomChoice(this.channels);
        const objective = this.randomChoice(this.objectives);
        const vertical = this.randomChoice(this.verticals);
        
        return {
            id: id,
            name: this.generateCampaignName(),
            category: category,
            technology: tech,
            channel: channel,
            objective: objective,
            vertical: vertical,
            description: this.generateDescription(category, tech, channel),
            budget: this.generateBudget(),
            timeline: this.generateTimeline(),
            metrics: this.generateMetrics(),
            success_probability: parseFloat(this.randomFloat(0.65, 0.95).toFixed(2)),
            complexity: this.randomChoice(["Baja", "Media", "Alta"]),
            priority: this.randomChoice(["Baja", "Media", "Alta", "Crítica"]),
            tags: [category, tech, channel, vertical],
            created_at: new Date().toISOString().replace('T', ' ').substring(0, 19)
        };
    }
    
    generateAllCampaigns(total = 1000) {
        const campaigns = [];
        
        console.log(`Generando ${total} campañas de marketing con IA...`);
        
        for (let i = 1; i <= total; i++) {
            const campaign = this.generateSingleCampaign(i);
            campaigns.push(campaign);
            
            if (i % 100 === 0) {
                console.log(`Progreso: ${i}/${total} campañas generadas`);
            }
        }
        
        console.log(`¡Completado! Se generaron ${campaigns.length} campañas exitosamente.`);
        return campaigns;
    }
    
    saveCampaigns(campaigns) {
        // Guardar JSON completo
        fs.writeFileSync('ai_marketing_campaigns.json', JSON.stringify(campaigns, null, 2), 'utf8');
        
        // Guardar CSV
        let csvContent = "ID,Nombre,Categoría,Tecnología,Canal,Objetivo,Presupuesto,Probabilidad_Éxito,Complejidad,Prioridad\n";
        campaigns.forEach(campaign => {
            csvContent += `${campaign.id},"${campaign.name}","${campaign.category}","${campaign.technology}","${campaign.channel}","${campaign.objective}",${campaign.budget.amount},${campaign.success_probability},"${campaign.complexity}","${campaign.priority}"\n`;
        });
        fs.writeFileSync('ai_marketing_campaigns.csv', csvContent, 'utf8');
        
        // Guardar resumen por categorías
        const categoriesSummary = {};
        campaigns.forEach(campaign => {
            const category = campaign.category;
            if (!categoriesSummary[category]) {
                categoriesSummary[category] = [];
            }
            categoriesSummary[category].push({
                id: campaign.id,
                name: campaign.name,
                budget: campaign.budget.amount,
                success_probability: campaign.success_probability
            });
        });
        fs.writeFileSync('campaigns_by_category.json', JSON.stringify(categoriesSummary, null, 2), 'utf8');
        
        console.log("Archivos guardados:");
        console.log("- ai_marketing_campaigns.json (completo)");
        console.log("- ai_marketing_campaigns.csv (para análisis)");
        console.log("- campaigns_by_category.json (por categorías)");
    }
    
    generateStatistics(campaigns) {
        console.log("\n=== ESTADÍSTICAS DE CAMPAÑAS ===");
        console.log(`Total de campañas: ${campaigns.length}`);
        
        // Estadísticas por categoría
        const categories = {};
        campaigns.forEach(campaign => {
            const cat = campaign.category;
            categories[cat] = (categories[cat] || 0) + 1;
        });
        
        console.log("\nCampañas por categoría:");
        Object.entries(categories)
            .sort(([,a], [,b]) => b - a)
            .forEach(([cat, count]) => {
                console.log(`  ${cat}: ${count}`);
            });
        
        // Estadísticas por complejidad
        const complexity = {};
        campaigns.forEach(campaign => {
            const comp = campaign.complexity;
            complexity[comp] = (complexity[comp] || 0) + 1;
        });
        
        console.log("\nCampañas por complejidad:");
        Object.entries(complexity).forEach(([comp, count]) => {
            console.log(`  ${comp}: ${count}`);
        });
        
        // Presupuesto total
        const totalBudget = campaigns.reduce((sum, campaign) => sum + campaign.budget.amount, 0);
        console.log(`\nPresupuesto total estimado: $${totalBudget.toLocaleString()} USD`);
        console.log(`Presupuesto promedio por campaña: $${(totalBudget / campaigns.length).toFixed(2)} USD`);
    }
}

// Ejecutar generación
const generator = new AICampaignGenerator();
const campaigns = generator.generateAllCampaigns(1000);
generator.saveCampaigns(campaigns);
generator.generateStatistics(campaigns);


