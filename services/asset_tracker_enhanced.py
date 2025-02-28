from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import networkx as nx
from sqlalchemy import desc

class AssetTracker:
    def __init__(self, db_session):
        self.db_session = db_session
    
    def get_asset_details(self, asset_id):
        """Get detailed information about an asset"""
        from asset_tracker import Asset, AssetDependency
        
        asset = self.db_session.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            return None
        
        # Get dependent assets (assets that depend on this one)
        dependent_assets = self.db_session.query(Asset).join(
            AssetDependency, Asset.id == AssetDependency.asset_id
        ).filter(
            AssetDependency.depends_on_id == asset_id
        ).all()
        
        # Get dependencies (assets this one depends on)
        dependencies = self.db_session.query(Asset).join(
            AssetDependency, Asset.id == AssetDependency.depends_on_id
        ).filter(
            AssetDependency.asset_id == asset_id
        ).all()
        
        return {
            "asset": asset,
            "dependent_assets": dependent_assets,
            "dependencies": dependencies
        }
    
    def add_dependency(self, asset_id, depends_on_id):
        """Add a dependency between two assets"""
        from asset_tracker import AssetDependency
        
        # Check if dependency already exists
        existing = self.db_session.query(AssetDependency).filter(
            AssetDependency.asset_id == asset_id,
            AssetDependency.depends_on_id == depends_on_id
        ).first()
        
        if existing:
            return {"success": False, "message": "Dependency already exists"}
        
        # Check for circular dependencies
        if self._would_create_circular_dependency(asset_id, depends_on_id):
            return {"success": False, "message": "This would create a circular dependency"}
        
        # Create new dependency
        dependency = AssetDependency(
            asset_id=asset_id,
            depends_on_id=depends_on_id
        )
        self.db_session.add(dependency)
        self.db_session.commit()
        
        return {"success": True, "dependency_id": dependency.id}
    
    def _would_create_circular_dependency(self, asset_id, depends_on_id):
        """Check if adding a dependency would create a circular reference"""
        from asset_tracker import AssetDependency
        
        # If these are the same asset, it's circular by definition
        if asset_id == depends_on_id:
            return True
        
        # Build a directed graph of all dependencies
        G = nx.DiGraph()
        
        # Add all existing dependencies
        dependencies = self.db_session.query(AssetDependency).all()
        for dep in dependencies:
            G.add_edge(dep.asset_id, dep.depends_on_id)
        
        # Add the new proposed dependency
        G.add_edge(asset_id, depends_on_id)
        
        # Check for cycles
        try:
            nx.find_cycle(G)
            return True  # Cycle found
        except nx.NetworkXNoCycle:
            return False  # No cycle
    
    def remove_dependency(self, asset_id, depends_on_id):
        """Remove a dependency between two assets"""
        from asset_tracker import AssetDependency
        
        dependency = self.db_session.query(AssetDependency).filter(
            AssetDependency.asset_id == asset_id,
            AssetDependency.depends_on_id == depends_on_id
        ).first()
        
        if not dependency:
            return {"success": False, "message": "Dependency not found"}
        
        self.db_session.delete(dependency)
        self.db_session.commit()
        
        return {"success": True}
    
    def visualize_asset_dependencies(self, project_id):
        """Create a network graph of asset dependencies for a project"""
        from asset_tracker import Asset, AssetDependency, AssetStatus
        
        # Get all assets for the project
        assets = self.db_session.query(Asset).filter(Asset.project_id == project_id).all()
        asset_ids = [a.id for a in assets]
        
        # If no assets, return None
        if not assets:
            return None
        
        # Get all dependencies between these assets
        dependencies = self.db_session.query(AssetDependency).filter(
            AssetDependency.asset_id.in_(asset_ids),
            AssetDependency.depends_on_id.in_(asset_ids)
        ).all()
        
        # Create a graph
        G = nx.DiGraph()
        
        # Add nodes with attributes
        for asset in assets:
            G.add_node(
                asset.id, 
                name=asset.name,
                status=asset.status.value,
                progress=asset.progress,
                type=asset.asset_type.value
            )
        
        # Add edges
        for dep in dependencies:
            G.add_edge(dep.asset_id, dep.depends_on_id)
        
        # Generate positions
        pos = nx.spring_layout(G)
        
        # Create node traces by status
        status_colors = {
            "not_started": "gray",
            "in_progress": "blue",
            "review": "orange",
            "complete": "green"
        }
        
        # Create edge trace
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        # Create node traces by status
        node_traces = []
        for status, color in status_colors.items():
            # Filter nodes by status
            nodes = [n for n, attrs in G.nodes(data=True) if attrs.get('status') == status]
            
            if not nodes:
                continue
                
            node_x = []
            node_y = []
            node_text = []
            node_size = []
            
            for node in nodes:
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                
                # Get node attributes for hover text
                attrs = G.nodes[node]
                progress = attrs.get('progress', 0)
                node_size.append(15 + (progress / 10))  # Size based on progress
                
                # Create hover text
                hover_text = f"ID: {node}<br>Name: {attrs.get('name')}<br>"
                hover_text += f"Type: {attrs.get('type')}<br>Status: {status}<br>"
                hover_text += f"Progress: {progress}%"
                node_text.append(hover_text)
            
            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers',
                hoverinfo='text',
                text=node_text,
                marker=dict(
                    color=color,
                    size=node_size,
                    line_width=2
                ),
                name=status.replace('_', ' ').title()
            )
            
            node_traces.append(node_trace)
        
        # Create figure
        fig = go.Figure(
            data=[edge_trace] + node_traces,
            layout=go.Layout(
                title=f'Asset Dependencies for Project {project_id}',
                showlegend=True,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
        )
        
        return fig
    
    def find_critical_path(self, project_id):
        """Find the critical path of assets that are blocking project completion"""
        from asset_tracker import Asset, AssetDependency, AssetStatus
        
        # Get all assets for the project
        assets = self.db_session.query(Asset).filter(Asset.project_id == project_id).all()
        asset_map = {a.id: a for a in assets}
        asset_ids = list(asset_map.keys())
        
        # If no assets, return empty result
        if not assets:
            return {"success": False, "message": "No assets found for this project"}
        
        # Get all dependencies
        dependencies = self.db_session.query(AssetDependency).filter(
            AssetDependency.asset_id.in_(asset_ids),
            AssetDependency.depends_on_id.in_(asset_ids)
        ).all()
        
        # Create a directed graph
        G = nx.DiGraph()
        
        # Add all assets as nodes
        for asset in assets:
            # Weight is remaining work (100 - progress)
            G.add_node(asset.id, weight=100 - asset.progress)
        
        # Add dependencies as edges
        for dep in dependencies:
            G.add_edge(dep.asset_id, dep.depends_on_id)
        
        # Find all leaf nodes (assets that don't depend on any other assets)
        leaf_nodes = [n for n in G.nodes() if G.out_degree(n) == 0]
        
        # Find all root nodes (assets that no other assets depend on)
        root_nodes = [n for n in G.nodes() if G.in_degree(n) == 0]
        
        # If there are no clear paths, return all incomplete assets sorted by progress
        if not leaf_nodes or not root_nodes:
            incomplete_assets = [a for a in assets if a.status != AssetStatus.COMPLETE]
            incomplete_assets.sort(key=lambda x: x.progress)
            
            return {
                "success": True,
                "critical_path": [
                    {
                        "id": a.id,
                        "name": a.name,
                        "status": a.status.value,
                        "progress": a.progress
                    } for a in incomplete_assets
                ],
                "total_remaining_work": sum(100 - a.progress for a in incomplete_assets)
            }
        
        # For each leaf node, find the longest path from any root node
        critical_path = []
        max_length = 0
        max_weight = 0
        
        for leaf in leaf_nodes:
            for root in root_nodes:
                try:
                    paths = list(nx.all_simple_paths(G, root, leaf))
                    
                    for path in paths:
                        path_length = len(path)
                        path_weight = sum(G.nodes[n]['weight'] for n in path)
                        
                        if path_weight > max_weight or (path_weight == max_weight and path_length > max_length):
                            critical_path = path
                            max_length = path_length
                            max_weight = path_weight
                except nx.NetworkXNoPath:
                    continue
        
        # Convert node IDs to asset details
        critical_assets = []
        for asset_id in critical_path:
            asset = asset_map[asset_id]
            critical_assets.append({
                "id": asset.id,
                "name": asset.name,
                "status": asset.status.value,
                "progress": asset.progress,
                "remaining": 100 - asset.progress
            })
        
        return {
            "success": True,
            "critical_path": critical_assets,
            "total_remaining_work": max_weight
        }
    
    def create_burndown_chart(self, project_id, start_date, end_date):
        """Create a burndown chart showing asset completion over time"""
        from asset_tracker import Asset, AssetStatus
        
        # Get all assets for the project
        assets = self.db_session.query(Asset).filter(Asset.project_id == project_id).all()
        
        # If no assets, return None
        if not assets:
            return None
        
        # Create a date range for the full project
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        date_range = [start + timedelta(days=x) for x in range((end-start).days + 1)]
        
        # Ideal burndown - linear from total assets to 0
        total_assets = len(assets)
        ideal_per_day = total_assets / len(date_range) if date_range else 0
        ideal_remaining = [total_assets - (i * ideal_per_day) for i in range(len(date_range))]
        
        # Get current date index
        today = datetime.now().date()
        today_index = next((i for i, d in enumerate(date_range) if d.date() >= today), len(date_range) - 1)
        
        # Calculate actual burndown (completed assets per day)
        # In a real system, you would track when assets were marked complete
        # For this example, we'll use random completion dates
        import random
        random.seed(42)  # For reproducible results
        
        completed_assets = []
        for asset in assets:
            if asset.status == AssetStatus.COMPLETE:
                # Assign a random completion date in the past
                completion_day = random.randint(0, today_index)
                completed_assets.append((asset.id, date_range[completion_day]))
        
        # Sort by completion date
        completed_assets.sort(key=lambda x: x[1])
        
        # Calculate remaining assets by day
        actual_remaining = []
        completed_count = 0
        
        for day in date_range:
            completed_on_day = sum(1 for _, completion_date in completed_assets if completion_date.date() <= day.date())
            actual_remaining.append(total_assets - completed_on_day)
        
        # Create DataFrame for plotting
        df = pd.DataFrame({
            'date': date_range,
            'ideal_remaining': ideal_remaining,
            'actual_remaining': actual_remaining
        })
        
        # Create the figure
        fig = go.Figure()
        
        # Add ideal burndown line
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['ideal_remaining'],
            name='Ideal Burndown',
            line=dict(color='green', width=2, dash='dash')
        ))
        
        # Add actual burndown line
        fig.add_trace(go.Scatter(
            x=df['date'][:today_index+1],
            y=df['actual_remaining'][:today_index+1],
            name='Actual Burndown',
            line=dict(color='blue', width=2)
        ))
        
        # Add projected burndown if project is still in progress
        if today_index < len(date_range) - 1 and today_index > 0:
            # Calculate burn rate based on recent progress
            recent_period = min(10, today_index)
            recent_completed = df['actual_remaining'][today_index - recent_period] - df['actual_remaining'][today_index]
            recent_burn_rate = recent_completed / recent_period if recent_period > 0 else 0
            
            # Project future burndown
            projected_remaining = []
            for i in range(today_index, len(date_range)):
                days_from_today = i - today_index
                projected = max(0, df['actual_remaining'][today_index] - (days_from_today * recent_burn_rate))
                projected_remaining.append(projected)
            
            # Add projected burndown line
            fig.add_trace(go.Scatter(
                x=df['date'][today_index:],
                y=projected_remaining,
                name='Projected Burndown',
                line=dict(color='red', width=2, dash='dot')
            ))
            
            # Calculate projected completion date
            if recent_burn_rate > 0:
                days_to_completion = df['actual_remaining'][today_index] / recent_burn_rate
                projected_completion = date_range[today_index].date() + timedelta(days=days_to_completion)
                
                if projected_completion <= end.date():
                    fig.add_vline(
                        x=projected_completion, 
                        line_width=2, 
                        line_dash="dash", 
                        line_color="red",
                        annotation_text="Projected Completion", 
                        annotation_position="top right"
                    )
                else:
                    # Add an annotation that project will likely extend beyond end date
                    fig.add_annotation(
                        x=end.date(),
                        y=projected_remaining[-1],
                        text=f"Projected to extend beyond end date by {(projected_completion - end.date()).days} days",
                        showarrow=True,
                        arrowhead=1,
                        ax=0,
                        ay=-40
                    )
        
        # Update layout
        fig.update_layout(
            title='Asset Burndown Chart',
            xaxis_title='Date',
            yaxis_title='Remaining Assets',
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig 